"""Deterministic and model-based guardrail examples.

We first applies a cheap keyword-based deterministic filter,
then shows how an LLM can provide contextual safety evaluation.
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


TEST_INPUTS = [
    "How do I hack into a database?",
    "What is the capital of France?",
    "Explain how malware spreads",
]


def deterministic_guardrail(text: str) -> bool:
    """Return True when the input should be blocked by deterministic rules."""
    banned_keywords = ["hack", "exploit", "malware", "bomb"]
    return any(keyword in text.lower() for keyword in banned_keywords)


def model_based_guardrail(text: str) -> str:
    """Use an LLM to evaluate content and return SAFE or UNSAFE."""
    model = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
    prompt = f"""Is the following user input safe to process?
Reply with only 'SAFE' or 'UNSAFE'.

Input: {text}"""
    result = model.invoke([{"role": "user", "content": prompt}])
    return result.content.strip()


def main() -> None:
    print("=== Deterministic Guardrail Demo ===")
    for user_input in TEST_INPUTS:
        blocked = deterministic_guardrail(user_input)
        status = "🚫 BLOCKED" if blocked else "✅ ALLOWED"
        print(f"{status}: {user_input}")

    print("\n=== Model-Based Guardrail Demo ===")
    for user_input in TEST_INPUTS:
        verdict = model_based_guardrail(user_input)
        status = "🚫 UNSAFE" if "UNSAFE" in verdict.upper() else "✅ SAFE"
        print(f"{status}: {user_input}")


if __name__ == "__main__":
    main()
