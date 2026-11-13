from Agents.flight_agent import flight_agent
from Agents.hotel_agent import hotel_agent
from Agents.itenary_agent import itinerary_agent
from Agents.weather_agent import weather_agent
from Agents.final_agent import final_agent
from Agents.supervisor_agent import supervisor_agent

from langgraph.graph import StateGraph, START, END

from gaurdrail import input_guardrail, guardrail_rejection
from human_in_loop import prepare_approval, human_approval, route_after_approval, approval_rejection

from routing import route_after_agent, route_after_guardrail, route_from_supervisor

from travel_state import TravelState

    
# ==========================================
# BUILD LANGGRAPH WORKFLOW
# ==========================================



graph = StateGraph(TravelState)


# ------------------------------------------
# 1. Register all nodes
# ------------------------------------------

graph.add_node("input_guardrail", input_guardrail)

graph.add_node("supervisor_agent", supervisor_agent)

graph.add_node("guardrail_rejection", guardrail_rejection)

graph.add_node("flight_agent", flight_agent)

graph.add_node("hotel_agent", hotel_agent)

graph.add_node("weather_agent", weather_agent)

graph.add_node("itinerary_agent", itinerary_agent)

graph.add_node("prepare_approval", prepare_approval)

graph.add_node("human_approval", human_approval)

graph.add_node("approval_rejection", approval_rejection)

graph.add_node("final_agent", final_agent)


# ------------------------------------------
# 2. START -> Input Guardrail
# ------------------------------------------

graph.add_edge(START, "input_guardrail")


# ------------------------------------------
# 3. Input Guardrail Routing
# ------------------------------------------

graph.add_conditional_edges(
    "input_guardrail",
    route_after_guardrail,
    {
        "supervisor_agent": "supervisor_agent",
        "guardrail_rejection": "guardrail_rejection"
    }
)


# Rejected request -> END

graph.add_edge("guardrail_rejection", END)


# ------------------------------------------
# 4. Supervisor Routing
# ------------------------------------------

agent_routes = {
    "flight_agent": "flight_agent",
    "hotel_agent": "hotel_agent",
    "weather_agent": "weather_agent",
    "itinerary_agent": "itinerary_agent"
}

graph.add_conditional_edges(
    "supervisor_agent",
    route_from_supervisor,
    agent_routes
)


# ------------------------------------------
# 5. Dynamic Agent Routing
# ------------------------------------------

for agent in [
    "flight_agent",
    "hotel_agent",
    "weather_agent",
    "itinerary_agent"
]:

    graph.add_conditional_edges(
        agent,
        route_after_agent(agent),
        {
            **agent_routes,
            "prepare_approval": "prepare_approval",
            "final_agent": "final_agent"
        }
    )


# ------------------------------------------
# 6. Prepare Approval -> Human Approval
# ------------------------------------------

graph.add_edge(
    "prepare_approval",
    "human_approval"
)


# ------------------------------------------
# 7. Human Approval Routing
# ------------------------------------------

graph.add_conditional_edges(
    "human_approval",
    route_after_approval,
    {
        "final_agent": "final_agent",
        "approval_rejection": "approval_rejection"
    }
)


# Rejected itinerary -> END

graph.add_edge("approval_rejection", END)


# ------------------------------------------
# 8. Final Agent -> END
# ------------------------------------------

graph.add_edge("final_agent", END)