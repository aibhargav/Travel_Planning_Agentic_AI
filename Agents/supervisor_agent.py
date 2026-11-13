# =========================
# Supervisor Agent
# =========================

import json

from travel_state import TravelState
from llm_call import llm

from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)

async def supervisor_agent(state: TravelState):

    print("\nINSIDE SUPERVISOR AGENT\n")

    query = state["user_query"]

    supervisor_prompt = f"""
You are the Supervisor Agent of a Travel Planning AI system.

Your responsibility is to understand the user's travel request
and select the appropriate specialist agents.

Available agents:

1. flight_agent
   - Flight information
   - Airports and airlines
   - Flight routes and travel duration

2. hotel_agent
   - Hotel recommendations
   - Accommodation and stays

3. weather_agent
   - Current weather
   - Weather forecasts
   - Destination weather information

4. itinerary_agent
   - Complete travel itinerary
   - Day-by-day travel planning
   - Organizing a complete trip

Rules:

- Select ONLY the agents required for the user's request.
- For a complete trip planning request, select all relevant
  specialist agents.
- For a weather-only request, select only weather_agent.
- For a flight-only request, select only flight_agent.
- For a hotel-only request, select only hotel_agent.
- Include itinerary_agent when the user requests a trip plan
  or day-by-day itinerary.
- Do not select final_agent. It executes separately.
- Maintain this execution order:
  flight_agent, hotel_agent, weather_agent, itinerary_agent.
- If multiple agents are required, include all of them
  in the requested_agents list.

Return ONLY valid JSON in this format:

{{
    "requested_agents": [
        "flight_agent",
        "hotel_agent"
    ],
    "reason": "Brief explanation"
}}

User Request:
{query}
"""

    try:

        response = await llm.ainvoke([
            SystemMessage(
                content="You are an intelligent travel supervisor. "
                        "Return valid JSON only."
            ),
            HumanMessage(content=supervisor_prompt)
        ])

        result = json.loads(response.content)

        # Only allow registered agent names
        valid_agents = [
            "flight_agent",
            "hotel_agent",
            "weather_agent",
            "itinerary_agent"
        ]

        requested_agents = result.get("requested_agents", [])

        if not isinstance(requested_agents, list):
            raise ValueError("Invalid agent list")

        # Remove invalid agents and duplicates
        requested_agents = list(dict.fromkeys(
            agent for agent in requested_agents
            if agent in valid_agents
        ))

        if not requested_agents:
            raise ValueError("No valid agents selected")

        reason = result.get("reason", "")

        # Select the first agent for execution
        next_agent = requested_agents[0]

    except Exception as e:

        print(f"Supervisor Agent Error: {e}")

        # Fallback: execute all specialist agents
        requested_agents = [
            "flight_agent",
            "hotel_agent",
            "weather_agent",
            "itinerary_agent"
        ]

        next_agent = requested_agents[0]
        reason = "Supervisor fallback: executing all agents."

    print("\nSUPERVISOR DECISION")
    print("Selected Agents:", requested_agents)
    print("Reason:", reason)

    return {
        "requested_agents": requested_agents,
        "next_agent": next_agent,
        "llm_calls": state.get("llm_calls", 0) + 1
    }