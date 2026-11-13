# =========================
# Weather Agent
# =========================


from travel_state import TravelState
from llm_call import llm

from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)

from mcp_tools.weather_tools import destination_extraction_tool, current_weather_tool, forecast_weather_tool

async def weather_agent(state: TravelState):

    print("\nINSIDE WEATHER AGENT\n")

    city = await destination_extraction_tool(state["user_query"])

    weather_data = await current_weather_tool(city)

    forecast_data = await forecast_weather_tool(city)

    print(f"Current_weather_data: {weather_data}")

    print(f"forecast_weather_data: {forecast_data}")

    return {
        "weather_results": f"""
        Current Weather:
        {weather_data}

        Forecast:
        {forecast_data}
        """,
        "messages": [
            AIMessage(
                content="Weather information fetched"
            )
        ]
        
    }
