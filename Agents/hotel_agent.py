

from travel_state import TravelState
from llm_call import llm

from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)

from mcp_tools.tavily_tools import tavily_search_tool


# =========================
# Hotel Agent
# =========================

async def hotel_agent(state: TravelState):

    print("\nINSIDE HOTEL AGENT\n")

    query = f"Best hotels for {state['user_query']}"

    hotel_results = await tavily_search_tool(query)

    print(f"hotel_results: {hotel_results}")
    return {
        "hotel_results": hotel_results,
        "messages": [
            AIMessage(content="Hotel information fetched.")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

