"""Human-in-the-loop example using LangChain middleware."""

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

load_dotenv()


@tool
def search_documentation(query: str) -> str:
    """Safe, read-only search tool."""
    return f"Documentation search results for: {query}"


@tool
def issue_refund(customer_id: str, amount_usd: float) -> str:
    """High-risk action: transfers real financial value."""
    return f"Transferred ${amount_usd:.2f} refund to customer {customer_id}."


hitl_agent = create_agent(
    model=ChatGroq(model="openai/gpt-oss-20b", temperature=0),
    tools=[search_documentation, issue_refund],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "issue_refund": True,
                "search_documentation": False,
            }
        )
    ],
    checkpointer=InMemorySaver(),
)


def main() -> None:
    session_config = {"configurable": {"thread_id": "support_session_402"}}

    print("--- Trigger approval ---")
    response = hitl_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Issue a refund of $120.00 to customer CUST-9921.",
                }
            ]
        },
        config=session_config,
    )

    if "__interrupt__" in response:
        interrupt_data = response["__interrupt__"][0].value
        flagged_tool = interrupt_data["action_requests"][0]
        print(f"Execution Paused: Tool '{flagged_tool['name']}' requires sign-off.")
        print(f"Arguments: {flagged_tool['args']}")

    print("\n--- Approve ---")
    approved_response = hitl_agent.invoke(
        Command(resume={"decisions": [{"type": "approve"}]}),
        config=session_config,
    )
    print(approved_response["messages"][-1].content)

    print("\n--- Reject ---")
    reject_config = {"configurable": {"thread_id": "support_session_403"}}
    hitl_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Issue a refund of $5000.00 to customer CUST-1044.",
                }
            ]
        },
        config=reject_config,
    )

    rejected_response = hitl_agent.invoke(
        Command(
            resume={
                "decisions": [
                    {
                        "type": "reject",
                        "reason": "Refund amount exceeds policy limits.",
                    }
                ]
            }
        ),
        config=reject_config,
    )
    print(rejected_response["messages"][-1].content)


if __name__ == "__main__":
    main()
