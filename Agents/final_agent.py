# =========================
# Final Response Agent
# =========================


from travel_state import TravelState
from llm_call import llm

from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)

def final_agent(state: TravelState):

    print("\nINSIDE FINAL AGENT\n")

    requested_agents = state["requested_agents"]

    # Collect only the results from executed agents
    travel_information = []

    if "flight_agent" in requested_agents:
        travel_information.append(
            f"FLIGHT INFORMATION:\n{state['flight_results']}"
        )

    if "hotel_agent" in requested_agents:
        travel_information.append(
            f"HOTEL INFORMATION:\n{state['hotel_results']}"
        )

    if "weather_agent" in requested_agents:
        travel_information.append(
            f"WEATHER INFORMATION:\n{state['weather_results']}"
        )

    if "itinerary_agent" in requested_agents:
        travel_information.append(
            f"TRAVEL ITINERARY:\n{state['itinerary']}"
        )

    available_information = "\n\n".join(travel_information)

    final_prompt = f"""
You are a professional AI Travel Planning Assistant.

User Request:
{state['user_query']}

Information collected from the specialist agents:

{available_information}

Your responsibilities:

1. Answer the user's original request.
2. Use only the information provided by the specialist agents.
3. Do not invent flight prices, hotel availability,
   weather conditions or other factual details.
4. Do not generate sections for agents that were not executed.
5. If some information is unavailable, clearly mention it.
6. Format the response using clear headings and bullet points.
7. Keep the response useful, concise and practical.

Generate the final response.
"""

    response = llm.invoke([
        SystemMessage(
            content="You are a professional AI travel assistant."
        ),
        HumanMessage(content=final_prompt)
    ])

    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }
