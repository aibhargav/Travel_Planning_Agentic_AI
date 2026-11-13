# =========================
# Human-in-the-Loop
# =========================

from travel_state import TravelState
from langgraph.types import interrupt

from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)

def prepare_approval(state: TravelState):

    return {
        "requires_approval": True,
        "approval_status": "pending"
    }

def human_approval(state: TravelState):

    # Pause graph execution and request human decision
    decision = interrupt({
        "message": "Please review your generated travel itinerary.",
        "itinerary": state["itinerary"],
        "options": ["approve", "reject"]
    })

    # Extract the human's decision
    if isinstance(decision, dict):
        approval = decision.get("decision", "").lower()
        feedback = decision.get("feedback", "")
    else:
        approval = str(decision).lower()
        feedback = ""

    if approval == "approve":

        return {
            "requires_approval": False,
            "approval_status": "approved",
            "human_feedback": feedback
        }

    return {
        "requires_approval": False,
        "approval_status": "rejected",
        "human_feedback": feedback
    }


# =========================
# Route after Human Approval
# =========================

def route_after_approval(state: TravelState):

    if state["approval_status"] == "approved":
        return "final_agent"

    return "approval_rejection"


# =========================
# Rejection Response
# =========================

def approval_rejection(state: TravelState):

    return {
        "messages": [
            AIMessage(
                content=(
                    "Your travel itinerary was not approved. "
                    "Please provide a new request if you would "
                    "like to generate another itinerary."
                )
            )
        ]
    }
