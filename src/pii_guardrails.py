"""PII protection example using LangChain middleware."""

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain_core.tools import tool
from langchain_groq import ChatGroq

load_dotenv()


@tool
def lookup_customer_account(query: str) -> str:
    """Safe lookup operation for customer records."""
    return f"Account record retrieved for identifier: {query}"


pii_agent = create_agent(
    model=ChatGroq(model="openai/gpt-oss-20b", temperature=0),
    tools=[lookup_customer_account],
    middleware=[
        PIIMiddleware(
            "credit_card",
            strategy="mask",
            apply_to_input=True,
        ),
        PIIMiddleware(
            "email",
            strategy="redact",
            apply_to_input=True,
        ),
        PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-Z0-9]{32,}",
            strategy="block",
            apply_to_input=True,
        ),
    ],
)


def main() -> None:
    print("--- Masking and redaction ---")
    response = pii_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Verify card 5105-1051-0510-5100 and send update to user@example.com",
                }
            ]
        }
    )

    for message in response["messages"]:
        print(f"[{message.type.upper()}]: {message.content}")

    print("\n--- Strict blocking ---")
    try:
        pii_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "My secret key is sk-abcdefghijklmnopqrstuvwxyz123456",
                    }
                ]
            }
        )
    except Exception as error:
        print(f"Blocked: {error}")


if __name__ == "__main__":
    main()
