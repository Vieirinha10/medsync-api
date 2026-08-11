import calendar
import hmac
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from database import get_db
from models import (
    AsaasWebhookEvent,
    PaymentGrant,
    PaymentOrder,
    User,
    UserEntitlement,
)
from schemas import CheckoutCreate, CheckoutResponse, PaymentStatusResponse
from security import get_current_user
from services.asaas import AsaasApiError, AsaasConfigurationError, create_checkout
from settings import asaas_webhook_token, frontend_url

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])

PLANS = {
    "avulso": {
        "name": "MedSync Premium Mensal",
        "description": "30 dias de acesso Premium, sem renovação automática.",
        "amount_cents": 2590,
        "billing_type": "PIX",
        "charge_type": "DETACHED",
    },
    "recorrente": {
        "name": "MedSync Premium Recorrente",
        "description": "Acesso Premium com renovação automática mensal.",
        "amount_cents": 2390,
        "billing_type": "CREDIT_CARD",
        "charge_type": "RECURRENT",
    },
    "trimestral": {
        "name": "MedSync Premium Trimestral",
        "description": "Três meses de acesso Premium, parcelável em até 3 vezes.",
        "amount_cents": 6590,
        "billing_type": "CREDIT_CARD",
        "charge_type": "INSTALLMENT",
    },
}

PAID_EVENTS = {"PAYMENT_CONFIRMED", "PAYMENT_RECEIVED"}
SUSPENSION_EVENTS = {
    "PAYMENT_REFUNDED",
    "PAYMENT_CHARGEBACK_REQUESTED",
    "PAYMENT_CREDIT_CARD_CAPTURE_REFUSED",
}


def _utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def _add_months(value: datetime, months: int) -> datetime:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def _callback(order_id: str, result: str) -> str:
    return f"{frontend_url()}/pagamento/retorno?pedido={order_id}&resultado={result}"


def _checkout_payload(order: PaymentOrder) -> dict[str, Any]:
    plan = PLANS[order.plano_id]
    charge_types = [plan["charge_type"]]
    if order.plano_id == "trimestral":
        charge_types.insert(0, "DETACHED")
    payload: dict[str, Any] = {
        "billingTypes": [plan["billing_type"]],
        "chargeTypes": charge_types,
        "minutesToExpire": 60,
        "externalReference": order.id,
        "callback": {
            "successUrl": _callback(order.id, "sucesso"),
            "cancelUrl": _callback(order.id, "cancelado"),
            "expiredUrl": _callback(order.id, "expirado"),
        },
        "items": [
            {
                "name": plan["name"],
                "description": plan["description"],
                "quantity": 1,
                "value": plan["amount_cents"] / 100,
            }
        ],
    }
    if order.plano_id == "recorrente":
        payload["subscription"] = {
            "cycle": "MONTHLY",
            "nextDueDate": datetime.now(UTC).date().isoformat(),
        }
    elif order.plano_id == "trimestral":
        payload["installment"] = {"maxInstallmentCount": 3}
    return payload


def _is_premium_active(entitlement: UserEntitlement | None) -> bool:
    return bool(
        entitlement
        and entitlement.status == "ativo"
        and _utc(entitlement.valido_ate) > datetime.now(UTC)
    )


@router.post(
    "/checkout",
    response_model=CheckoutResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment_checkout(
    body: CheckoutCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = PLANS[body.plano_id]
    order = PaymentOrder(
        id=str(uuid.uuid4()),
        id_usuario=current_user.id,
        plano_id=body.plano_id,
        valor_centavos=plan["amount_cents"],
        tipo_cobranca=plan["charge_type"],
        forma_pagamento=plan["billing_type"],
    )
    db.add(order)
    db.flush()

    try:
        checkout = create_checkout(_checkout_payload(order))
    except AsaasConfigurationError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AsaasApiError as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    order.asaas_checkout_id = str(checkout["id"])
    order.checkout_url = str(checkout["link"])
    order.status = "aguardando_pagamento"
    db.commit()
    return {
        "pedido_id": order.id,
        "checkout_url": order.checkout_url,
        "status": order.status,
    }


@router.get("/pedidos/{order_id}", response_model=PaymentStatusResponse)
def get_payment_status(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.get(PaymentOrder, order_id)
    if order is None or order.id_usuario != current_user.id:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    entitlement = db.get(UserEntitlement, current_user.id)
    return {
        "pedido_id": order.id,
        "plano_id": order.plano_id,
        "status": order.status,
        "premium_ativo": _is_premium_active(entitlement),
        "premium_valido_ate": entitlement.valido_ate if entitlement else None,
    }


def _grant_access(db: Session, order: PaymentOrder, payment: dict[str, Any]) -> None:
    payment_id = str(payment.get("id") or "")
    if not payment_id or db.get(PaymentGrant, payment_id):
        return

    is_checkout_grant = payment_id.startswith("checkout:")
    if order.status == "pago":
        if is_checkout_grant or order.plano_id != "recorrente":
            return
        if str(order.ultimo_pagamento_asaas_id or "").startswith("checkout:"):
            entitlement = db.get(UserEntitlement, order.id_usuario)
            if entitlement and payment.get("subscription"):
                entitlement.asaas_subscription_id = payment["subscription"]
            order.ultimo_pagamento_asaas_id = payment_id
            db.add(PaymentGrant(asaas_payment_id=payment_id, pedido_id=order.id))
            return

    now = datetime.now(UTC)
    entitlement = db.get(UserEntitlement, order.id_usuario)
    if entitlement is None:
        entitlement = UserEntitlement(
            id_usuario=order.id_usuario,
            plano_id=order.plano_id,
            valido_ate=now,
        )
        db.add(entitlement)

    current_expiry = _utc(entitlement.valido_ate)
    base = max(now, current_expiry) if entitlement.status == "ativo" else now
    if order.plano_id == "avulso":
        entitlement.valido_ate = base + timedelta(days=30)
    elif order.plano_id == "trimestral":
        entitlement.valido_ate = _add_months(base, 3)
    else:
        entitlement.valido_ate = _add_months(base, 1)

    entitlement.plano_id = order.plano_id
    entitlement.status = "ativo"
    entitlement.renovacao_automatica = order.plano_id == "recorrente"
    entitlement.asaas_subscription_id = payment.get("subscription")
    order.status = "pago"
    order.paid_at = order.paid_at or now
    order.ultimo_pagamento_asaas_id = payment_id
    db.add(PaymentGrant(asaas_payment_id=payment_id, pedido_id=order.id))


@router.post("/webhooks/asaas", status_code=status.HTTP_200_OK)
async def receive_asaas_webhook(
    request: Request,
    asaas_token: str | None = Header(default=None, alias="asaas-access-token"),
    db: Session = Depends(get_db),
):
    configured_token = asaas_webhook_token()
    if not configured_token or not asaas_token or not hmac.compare_digest(
        configured_token, asaas_token
    ):
        raise HTTPException(status_code=401, detail="Webhook não autorizado.")

    payload = await request.json()
    event_id = str(payload.get("id") or "")
    event_type = str(payload.get("event") or "")
    if not event_id or not event_type:
        raise HTTPException(status_code=422, detail="Evento da Asaas inválido.")
    duplicate_event = db.get(AsaasWebhookEvent, event_id)
    if duplicate_event and event_type != "CHECKOUT_PAID":
        return {"received": True, "duplicate": True}
    if duplicate_event is None:
        event = AsaasWebhookEvent(id=event_id, tipo=event_type, payload=payload)
        db.add(event)

    checkout = payload.get("checkout") or {}
    payment = payload.get("payment") or {}
    order = None
    checkout_id = checkout.get("id")
    external_reference = payment.get("externalReference") or checkout.get(
        "externalReference"
    )
    if external_reference:
        order = db.get(PaymentOrder, str(external_reference))
    if order is None and checkout_id:
        order = db.query(PaymentOrder).filter_by(asaas_checkout_id=str(checkout_id)).first()

    if order:
        checkout_statuses = {
            "CHECKOUT_CREATED": "aguardando_pagamento",
            "CHECKOUT_CANCELED": "cancelado",
            "CHECKOUT_EXPIRED": "expirado",
        }
        if event_type in checkout_statuses:
            order.status = checkout_statuses[event_type]
        elif event_type == "CHECKOUT_PAID":
            _grant_access(
                db,
                order,
                {"id": f"checkout:{checkout_id}"},
            )
        elif event_type in PAID_EVENTS:
            _grant_access(db, order, payment)
        elif event_type in SUSPENSION_EVENTS:
            order.status = "estornado" if event_type == "PAYMENT_REFUNDED" else "suspenso"
            entitlement = db.get(UserEntitlement, order.id_usuario)
            if (
                entitlement
                and order.ultimo_pagamento_asaas_id == payment.get("id")
            ):
                entitlement.status = "suspenso"

    db.commit()
    return {"received": True, "duplicate": duplicate_event is not None}
