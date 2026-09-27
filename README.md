# Production-Ready Agents: PII Protection & Human-in-the-Loop Guardrails

Code examples accompanying the Medium article **“Production-Ready Agents: Implementing PII Protection and Human-in-the-Loop Guardrails.”**

This repository demonstrates three practical safety patterns for LangChain agents:

- **Deterministic guardrails** — fast, rule-based checks such as keyword filtering.
- **Model-based guardrails** — LLM-based evaluation for cases that require contextual interpretation.
- **PII protection** with `PIIMiddleware` — mask, redact, or block sensitive information before it reaches the model.
- **Human-in-the-loop (HITL)** with `HumanInTheLoopMiddleware` — pause high-impact tool calls until a human explicitly approves or rejects them.

The deterministic/model-based example is intentionally simple so that the difference between the two approaches is easy to see. The PII and HITL examples then show how these ideas can be implemented with LangChain middleware.

## Project structure

```text
production-ready-agents-guardrails/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── src/
    ├── deterministic_vs_model_guardrails.py
    ├── pii_guardrails.py
    └── hitl_guardrails.py
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/LasithaAmarasinghe/PII-Protection-Human-in-the-Loop-Guardrails.git
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

The deterministic example works without an API key. The model-based, PII, and HITL examples use a Groq-hosted Llama model.

Copy `.env.example` to `.env` and add your Groq API key:

```bash
cp .env.example .env
```

Never commit `.env` or API keys to Git.

## Run the examples

### 1. Deterministic vs. model-based guardrails

```bash
python src/deterministic_vs_model_guardrails.py
```

The example demonstrates the same test inputs being evaluated in two ways:

**Deterministic:** a fixed list of keywords (`hack`, `exploit`, `malware`, `bomb`) is checked directly in the input.

**Model-based:** an LLM is asked to evaluate the input and return `SAFE` or `UNSAFE`.

The key idea is that deterministic rules are cheap and predictable, while model-based guardrails can handle more contextual cases. In a production pipeline, deterministic checks can be placed first, with model-based evaluation reserved for cases that need semantic interpretation.

### 2. PII middleware

```bash
python src/pii_guardrails.py
```

The example demonstrates:

1. Credit-card masking.
2. Email redaction.
3. API-key blocking.

### 3. Human-in-the-loop middleware

```bash
python src/hitl_guardrails.py
```

The example demonstrates:

1. A read-only tool that can execute automatically.
2. A refund tool that pauses for approval.
3. Approval using `Command(resume=...)`.
4. Rejection with a human-provided reason.

## Architecture

```text
                         ┌──────────────────────────┐
                         │       User Prompt        │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │   Deterministic Rules    │
                         │   Fast / cheap filters   │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │   Model-Based Guardrail  │
                         │ Contextual safety check  │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │      Input Middleware    │
                         │   Mask / Redact / Block  │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │      Agent Core (LLM)    │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │      Tool Middleware     │
                         │ Pause high-impact tools  │
                         └────────────┬─────────────┘
                                      │
                              Human Approval
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │     Output Middleware    │
                         │    Validate / sanitize   │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │      User Response       │
                         └──────────────────────────┘
```

## Production notes

- **Run deterministic filters first:** Use simple rules to catch obvious risks with low latency and cost.
- **Use model-based checks selectively:** Reserve semantic evaluation for cases where deterministic rules are insufficient.
- **Scrub inputs early:** Use `PIIMiddleware` at the entrance of your pipeline so sensitive identifiers do not unnecessarily enter model context.
- **Protect more than the initial input:** Sensitive information can re-enter a workflow through tool results, databases, logs, traces, and model-generated content.
- **Maintain persistent checkpointers:** The HITL example uses `InMemorySaver` for simplicity. Production deployments should use persistent storage so interrupted sessions survive application restarts.
- **Separate read from write:** Keep read-only tools autonomous and reserve human approval for state-altering or high-impact actions.

## Article

See the accompanying Medium article for the explanation, diagrams, and detailed walkthrough.

> `https://medium.com/@amarasinghelra/production-ready-agents-implementing-pii-protection-and-human-in-the-loop-guardrails`

## License

MIT License — see `LICENSE`.
