
import os
import json
import asyncio
from datetime import date

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()


async def test_realtime_flights():

    aviation_env = os.environ.copy()
    aviation_env["AVIATION_STACK_API_KEY"] = os.getenv(
        "AVIATIONSTACK_API_KEY", ""
    )

    client = MultiServerMCPClient({
        "aviationstack": {
            "transport": "stdio",
            "command": "uvx",
            "args": ["aviationstack-mcp"],
            "env": aviation_env
        }
    })

    try:
        # Connect to AviationStack MCP
        tools = await client.get_tools(server_name="aviationstack")

        tools_by_name = {
            tool.name: tool for tool in tools
        }

        # Select today's departure schedule tool
        flight_tool = tools_by_name[
            "flight_arrival_departure_schedule"
        ]

        print("\nFetching today's HYD departure schedule...")

        # Only ONE API request
        result = await flight_tool.ainvoke({
            "airport_iata_code": "HYD",
            "schedule_type": "departure",
            "number_of_flights": 100
        })

        # Parse MCP response
        if isinstance(result, list):
            raw_text = next(
                item["text"]
                for item in result
                if item.get("type") == "text"
            )
            response = json.loads(raw_text)
        elif isinstance(result, dict):
            response = result
        else:
            response = json.loads(result)

        print("\nAPI STATUS:", response.get("ok"))

        if not response.get("ok"):
            print("API ERROR:", response.get("error"))
            return

        flights = response.get("data", [])

        print("TOTAL FLIGHTS:", response.get("count", len(flights)))

        # Display returned records
        print("\nTODAY'S DEPARTURE FLIGHTS:\n")

        for flight in flights:
            print(json.dumps(flight, indent=4))

        # Filter Hyderabad -> Mumbai
        destination_code = "BOM"

        matching_flights = [
            flight for flight in flights
            if str(flight.get("arrival_airport_code", "")).upper()
            == destination_code
        ]

        print("\nHYDERABAD TO MUMBAI FLIGHTS:\n")

        if matching_flights:
            for flight in matching_flights:
                print(json.dumps(flight, indent=4))
        else:
            print("No matching flights found in returned records.")

            if flights:
                print("\nAvailable response fields:")
                print(list(flights[0].keys()))

    except Exception as e:
        print("ERROR:", repr(e))


if __name__ == "__main__":
    asyncio.run(test_realtime_flights())
