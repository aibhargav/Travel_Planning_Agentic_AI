# =========================
# Conditional Routing
# =========================

from travel_state import TravelState



# 1. Route after Input Guardrail

def route_after_guardrail(state: TravelState):

    if state["is_safe"]:
        return "supervisor_agent"

    return "guardrail_rejection"


# 2. Route after Supervisor

def route_from_supervisor(state: TravelState):

    return state["next_agent"]


# 3. Route after each selected agent


def route_after_agent(current_agent):

    def router(state: TravelState):

        requested_agents = state["requested_agents"]

        current_index = requested_agents.index(current_agent)

        # Execute the next selected agent
        if current_index + 1 < len(requested_agents):
            return requested_agents[current_index + 1]

        # If itinerary was selected, request human approval
        if "itinerary_agent" in requested_agents:
            return "prepare_approval"

        # Otherwise, generate the final response
        return "final_agent"

    return router
