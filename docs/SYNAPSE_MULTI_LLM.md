# 🧠 Synapse Multi-LLM 5-Core — Guia de Arquitetura e Ativação

A **Synapse** possui uma arquitetura de **Consenso Multi-LLM (Junta Médica de IAs)** capaz de orquestrar até 5 das maiores redes neurais do mundo simultaneamente:

1. **OpenAI (ChatGPT)**: Estruturação de dados, rubricas rígidas e notas.
2. **Anthropic (Claude 3.5)**: Síntese pedagógica empática e raciocínio fisiopatológico.
3. **Google Gemini (Gemini 2.0 Flash)**: Validação de diretrizes em altíssima velocidade e multimodalidade.
4. **xAI (Grok 2 / Mini)**: Auditoria crítica de segurança, contraindicações e diagnósticos diferenciais.
5. **DeepSeek (R1 Reasoning)**: Raciocínio clínico profundo (*Chain-of-Thought*) de causa e efeito.

---

## ⚡ Como Funciona a Ativação Plug & Play

O sistema foi desenhado para **funcionar 100% sob demanda**:

- **Se apenas a `OPENAI_API_KEY` estiver preenchida:** O sistema funciona normalmente no modo individual OpenAI, sem erros e sem lentidão.
- **Ao preencher a chave de qualquer outro provedor no arquivo `.env`:** A Synapse detecta a chave ativa e passa a incluí-lo na Junta Médica automaticamente via chamadas assíncronas paralelas (`asyncio` / `ThreadPoolExecutor`).
- **Se um provedor falhar ou ficar sem créditos:** Os demais provedores assumem sem interromper a experiência do aluno.

---

## 🔑 Onde Obter as Chaves de API e Custos Médios

| Provedor | Modelo Padrão Recomendado | Onde Criar a Conta / Obter Chave | Custo Estimado por 1 Milhão de Tokens |
| :--- | :--- | :--- | :--- |
| **OpenAI** | `gpt-4o-mini` / `gpt-5.6-luna` | [platform.openai.com](https://platform.openai.com) | ~$0.15 input / $0.60 output |
| **Anthropic** | `claude-3-5-haiku-20241022` | [console.anthropic.com](https://console.anthropic.com) | ~$0.80 input / $4.00 output |
| **Google Gemini** | `gemini-2.0-flash` | [aistudio.google.com](https://aistudio.google.com) | ~$0.10 input / $0.40 output |
| **xAI** | `grok-2-mini` | [console.x.ai](https://console.x.ai) | ~$0.20 input / $1.00 output |
| **DeepSeek** | `deepseek-reasoner` (R1) | [platform.deepseek.com](https://platform.deepseek.com) | ~$0.55 input / $2.19 output |

> **Custo Médio por Simulação:** Menos de **R$ 0,05** quando todas as 5 IAs estão ativas simultaneamente.

---

## 🛠️ Como Ativar no `.env`

Abra o arquivo `.env` do backend (`medsync-api/.env`) e adicione as chaves que desejar:

```env
# 1. OpenAI (Já Ativo)
OPENAI_API_KEY=sk-...

# 2. Anthropic Claude (Opcional - Adicione quando recarregar)
ANTHROPIC_API_KEY=sk-ant-...
SYNAPSE_ANTHROPIC_MODEL=claude-3-5-haiku-20241022

# 3. Google Gemini (Opcional - Adicione quando recarregar)
GEMINI_API_KEY=AIzaSy...
SYNAPSE_GEMINI_MODEL=gemini-2.0-flash

# 4. xAI Grok (Opcional - Adicione quando recarregar)
XAI_API_KEY=xai-...
SYNAPSE_XAI_MODEL=grok-2-mini

# 5. DeepSeek R1 (Opcional - Adicione quando recarregar)
DEEPSEEK_API_KEY=sk-...
SYNAPSE_DEEPSEEK_MODEL=deepseek-reasoner
```

---

## 🧪 Como Testar a Conexão

Após inserir uma nova chave, você pode rodar a suite de testes no terminal do backend:

```powershell
python -m pytest tests/test_evaluation.py
```
