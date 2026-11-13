# =========================
# State
# =========================

from langchain_core.messages import AnyMessage

from typing import TypedDict, Annotated
import operator


class TravelState(TypedDict):
    # Conversation
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str

    # Existing agent results
    flight_results: str
    hotel_results: str
    weather_results: str
    itinerary: str
    llm_calls: int

    # Input Guardrail
    is_safe: bool
    safety_reason: str

    # Supervisor
    next_agent: str
    requested_agents: list[str]

    # Human-in-the-Loop
    requires_approval: bool
    approval_status: str
    human_feedback: str