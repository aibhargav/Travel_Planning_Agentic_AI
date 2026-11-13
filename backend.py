import os 
import certifi
from dotenv import load_dotenv


load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()


from langgraph.types import Command

import uuid


from psycopg import AsyncConnection
from psycopg.rows import dict_row
from travel_graph import graph
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver




from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)


from travel_database  import get_database_url


# =========================
# PostgreSQL Checkpointer
# =========================

DATABASE_URL = get_database_url()

_conn = None
checkpointer = None
travel_graph = None


async def initialize_travel_graph():

    global travel_graph, _conn, checkpointer

    _conn = await AsyncConnection.connect(
        DATABASE_URL,
        autocommit=True,
        row_factory=dict_row
    )

    checkpointer = AsyncPostgresSaver(_conn)

    await checkpointer.setup()

    travel_graph = graph.compile(
        checkpointer=checkpointer
    )

    print("Travel graph initialized successfully!")


async def close_travel_graph():

    global _conn

    if _conn is not None:
        await _conn.close()
        _conn = None

    print("PostgreSQL connection closed.")






def format_travel_result(result, thread_id):
    # Check whether LangGraph paused at an interrupt
    interrupts = result.get("__interrupt__", [])

    if interrupts:
        approval_data = interrupts[0].value

        return {
            "status": "approval_required",
            "approval_required": True,
            "thread_id": thread_id,
            "approval": approval_data,
            "itinerary": result.get("itinerary", ""),
            "llm_calls": result.get("llm_calls", 0)
        }

    # Graph completed normally
    messages = result.get("messages", [])

    final_answer = (
        messages[-1].content if messages else "No response generated."
    )

    return {
        "status": "completed",
        "approval_required": False,
        "thread_id": thread_id,
        "answer": final_answer,
        "flight_results": result.get("flight_results", ""),
        "hotel_results": result.get("hotel_results", ""),
        "weather_results": result.get("weather_results", ""),
        "itinerary": result.get("itinerary", ""),
        "llm_calls": result.get("llm_calls", 0)
    }


async def run_travel_agent(user_input: str, thread_id: str | None = None):

    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state = {
        "messages": [
            HumanMessage(content=user_input)
        ],
        "user_query": user_input,
        "flight_results": "",
        "hotel_results": "",
        "weather_results": "",
        "itinerary": "",
        "llm_calls": 0,

        "is_safe": False,
        "safety_reason": "",

        "next_agent": "",
        "requested_agents": [],

        "requires_approval": False,
        "approval_status": "not_required",
        "human_feedback": ""
    }

    result = await travel_graph.ainvoke(
        initial_state,
        config=config
    )

    return format_travel_result(result, thread_id)


async def resume_travel_agent(
    thread_id: str,
    decision: str,
    feedback: str = ""
):

    if decision not in ["approve", "reject"]:
        raise ValueError("Decision must be 'approve' or 'reject'.")

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = await travel_graph.ainvoke(
        Command(
            resume={
                "decision": decision,
                "feedback": feedback
            }
        ),
        config=config
    )

    return format_travel_result(result, thread_id)