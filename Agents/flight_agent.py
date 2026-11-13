
# =========================
# Flight Agent
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

from mcp_tools.aviation_tools import aviation_flight_tool

def parse_aviation_response(result):

    if isinstance(result, list):
        for item in result:
            if item.get("type") == "text":
                return json.loads(item["text"])

    if isinstance(result, dict):
        return result

    if isinstance(result, str):
        return json.loads(result)

    raise ValueError("Unexpected AviationStack response format")


async def flight_agent(state: TravelState):

    print("\nINSIDE FLIGHT AGENT\n")

    query = state["user_query"]

    try:
        # STEP 1: Extract origin and destination from user query

        extraction_prompt = f"""
        Extract the origin and destination airport IATA codes
        from the following travel request.

        User request: {query}

        Return ONLY valid JSON in this format:
        {{
            "origin_iata": "HYD",
            "destination_iata": "BOM"
        }}

        If either location is unclear, use null.
        Do not guess unknown airport codes.
        """

        extraction_response = await llm.ainvoke([
            SystemMessage(
                content="You are an expert at identifying airport codes."
            ),
            HumanMessage(content=extraction_prompt)
        ])

        response_text = extraction_response.content.strip()

        # Remove Markdown JSON code blocks
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            response_text = response_text.rsplit("```", 1)[0].strip()

        route = json.loads(response_text)

        origin = route.get("origin_iata")
        destination = route.get("destination_iata")

        if not origin or not destination:
            flight_data = (
                "Please provide both your departure and destination "
                "cities so I can find relevant flights."
            )

        else:
            # STEP 2: Fetch today's departure schedule

            result = await aviation_flight_tool(
                "flight_arrival_departure_schedule",
                {
                    "airport_iata_code": origin,
                    "schedule_type": "departure",
                    "number_of_flights": 100
                }
            )

            response = parse_aviation_response(result)

            # STEP 3: Check API response

            if not response.get("ok"):
                error = response.get("error", "Unknown API error")

                if "rate_limit" in error.lower():
                    flight_data = (
                        "Flight information is temporarily unavailable "
                        "because the API rate limit was reached."
                    )
                else:
                    flight_data = f"Flight API error: {error}"

            else:
                # STEP 4: Filter flights by destination

                flights = response.get("data", [])

                matching_flights = [
                    flight for flight in flights
                    if str(
                        flight.get("arrival_airport_code", "")
                    ).upper() == destination.upper()
                ]

                if not matching_flights:
                    flight_data = (
                        f"No flights from {origin} to {destination} "
                        "were found in the returned departure records."
                    )

                else:
                    # STEP 5: Ask LLM to format flight information

                    flight_prompt = f"""
                    You are an expert flight information assistant.

                    The following flight records were retrieved from AviationStack.

                        Origin: {origin}
                        Destination: {destination}

                        Flight records:
                        {json.dumps(matching_flights, indent=2)}

                    Present the flight information in a clean Markdown table.

                    Include:
                        - Airline
                        - Flight number
                        - Scheduled departure
                        - Estimated departure
                        - Actual departure
                        - Scheduled arrival
                        - Arrival terminal
                        - Departure delay

                    IMPORTANT RULES:

                    1. Never invent missing information.
                    2. If actual departure time is null, say
                         "Actual departure not reported".
                    3. Do not assume a flight has departed or is airborne
                       based only on missing actual departure time.
                    4. Do not claim ticket availability or provide ticket prices.
                    5. Do not treat similar flight records as separate
                        operated aircraft without evidence.
                    6. Clearly mention that the information comes from
                        AviationStack schedule data.
                    7. Do not make unsupported travel recommendations.

                    Provide a short summary after the table.
                    """

                

                    final_response = await llm.ainvoke([
                        SystemMessage(
                            content="You are an expert flight information assistant."
                        ),
                        HumanMessage(content=flight_prompt)
                    ])

                    flight_data = final_response.content

    except Exception as e:

        print(f"Flight Agent Error: {e}")

        flight_data = (
            "Unable to retrieve flight information at the moment. "
            "Please try again later."
        )
    print(f"flight_results: {flight_data}")
    return {
        "flight_results": flight_data,
        "messages": [
            AIMessage(content="Flight information retrieved")
        ],
        "llm_calls": state.get("llm_calls", 0) + 2
    }