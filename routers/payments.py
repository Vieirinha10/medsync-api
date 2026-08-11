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
from schemas import (
    CheckoutCreate,
    CheckoutResponse,
    PaymentStatusResponse,
    TransparentPaymentCreate,
    TransparentPaymentResponse,
)
from security import get_current_user
from services.asaas import (
    AsaasApiError,
    AsaasConfigurationError,
    create_checkout,
    create_customer,
    create_payment,
    create_subscription,
    get_pix_qr_code,
)
from settings import (
    asaas_environment,
    asaas_webhook_token,
    frontend_url,
    payment_pilot_emails,
    payments_enabled,
)

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
    "PAYMENT_REPROVED_BY_RISK_ANALYSIS",
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


def _check_payment_availability(current_user: User) -> None:
    if (
        asaas_environment() == "production"
        and not payments_enabled()
        and current_user.email.lower() not in payment_pilot_emails()
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Os pagamentos estão em liberação controlada. Tente novamente em breve.",
        )


def _payer_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if forwarded:
        return forwarded
    return request.client.host if request.client else "127.0.0.1"


def _customer_payload(current_user: User, body: TransparentPaymentCreate) -> dict[str, Any]:
    payer = body.pagador
    return {
        "name": current_user.nome,
        "email": current_user.email,
        "cpfCnpj": payer.cpf_cnpj,
        "mobilePhone": payer.telefone,
        "postalCode": payer.cep,
        "addressNumber": payer.numero_endereco,
        "complement": payer.complemento,
        "externalReference": f"medsync-user:{current_user.id}",
        "notificationDisabled": True,
    }


def _card_payload(body: TransparentPaymentCreate) -> dict[str, str]:
    assert body.cartao is not None
    card = body.cartao
    return {
        "holderName": card.titular,
        "number": card.numero.get_secret_value(),
        "expiryMonth": card.mes_validade,
        "expiryYear": card.ano_validade,
        "ccv": card.ccv.get_secret_value(),
    }


def _holder_payload(current_user: User, body: TransparentPaymentCreate) -> dict[str, str]:
    payer = body.pagador
    return {
        "name": body.cartao.titular if body.cartao else current_user.nome,
        "email": current_user.email,
        "cpfCnpj": payer.cpf_cnpj,
        "postalCode": payer.cep,
        "addressNumber": payer.numero_endereco,
        "addressComplement": payer.complemento or "",
        "mobilePhone": payer.telefone,
    }


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
    _check_payment_availability(current_user)

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


@router.post(
    "/transparente",
    response_model=TransparentPaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transparent_payment(
    body: TransparentPaymentCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Processa Pix ou cartão sem persistir os dados sensíveis do cartão."""
    _check_payment_availability(current_user)
    plan = PLANS[body.plano_id]
    order = PaymentOrder(
        id=str(uuid.uuid4()),
        id_usuario=current_user.id,
        plano_id=body.plano_id,
        valor_centavos=plan["amount_cents"],
        tipo_cobranca=plan["charge_type"],
        forma_pagamento=plan["billing_type"],
        status="processando",
    )
    db.add(order)
    db.commit()

    try:
        if not current_user.asaas_customer_id:
            customer = create_customer(_customer_payload(current_user, body))
            customer_id = str(customer.get("id") or "")
            if not customer_id:
                raise AsaasApiError("A Asaas não retornou o identificador do cliente.")
            current_user.asaas_customer_id = customer_id
            db.commit()

        common_payload: dict[str, Any] = {
            "customer": current_user.asaas_customer_id,
            "billingType": plan["billing_type"],
            "dueDate": datetime.now(UTC).date().isoformat(),
            "description": plan["description"],
            "externalReference": order.id,
        }

        if body.plano_id == "avulso":
            payment = create_payment(
                {**common_payload, "value": plan["amount_cents"] / 100}
            )
            payment_id = str(payment.get("id") or "")
            if not payment_id:
                raise AsaasApiError("A Asaas não retornou o identificador da cobrança.")
            qr_code = get_pix_qr_code(payment_id)
            order.ultimo_pagamento_asaas_id = payment_id
            order.status = "aguardando_pagamento"
            db.commit()
            return {
                "pedido_id": order.id,
                "forma_pagamento": "PIX",
                "status": order.status,
                "pix_qr_code": qr_code.get("encodedImage"),
                "pix_copia_cola": qr_code.get("payload"),
                "pix_expira_em": qr_code.get("expirationDate"),
            }

        card_fields = {
            "creditCard": _card_payload(body),
            "creditCardHolderInfo": _holder_payload(current_user, body),
            "remoteIp": _payer_ip(request),
        }
        if body.plano_id == "recorrente":
            transaction = create_subscription(
                {
                    "customer": current_user.asaas_customer_id,
                    "billingType": "CREDIT_CARD",
                    "description": plan["description"],
                    "externalReference": order.id,
                    **card_fields,
                    "value": plan["amount_cents"] / 100,
                    "cycle": "MONTHLY",
                    "nextDueDate": datetime.now(UTC).date().isoformat(),
                }
            )
            transaction_id = str(transaction.get("id") or "")
            if not transaction_id:
                raise AsaasApiError("A Asaas não retornou o identificador da assinatura.")
            order.ultimo_pagamento_asaas_id = transaction_id
        else:
            payment_payload = {**common_payload, **card_fields}
            if body.parcelas == 1:
                payment_payload["value"] = plan["amount_cents"] / 100
            else:
                payment_payload["installmentCount"] = body.parcelas
                payment_payload["totalValue"] = plan["amount_cents"] / 100
            transaction = create_payment(payment_payload)
            transaction_id = str(transaction.get("id") or "")
            if not transaction_id:
                raise AsaasApiError("A Asaas não retornou o identificador da cobrança.")
            order.ultimo_pagamento_asaas_id = transaction_id

        order.status = "aguardando_confirmacao"
        db.commit()
        return {
            "pedido_id": order.id,
            "forma_pagamento": "CREDIT_CARD",
            "status": order.status,
        }
    except AsaasConfigurationError as exc:
        order.status = "falhou"
        db.commit()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AsaasApiError as exc:
        order.status = "recusado"
        db.commit()
        message = str(exc)
        if body.plano_id != "avulso":
            message = "Pagamento não autorizado. Revise os dados ou tente outro cartão."
        raise HTTPException(status_code=422, detail=message) from exc


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
