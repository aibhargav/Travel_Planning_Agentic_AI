from pathlib import Path
import traceback
import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from backend import (
    run_travel_agent,
    initialize_travel_graph,
    close_travel_graph
)

from contextlib import asynccontextmanager


# This is to allow nested event loops for async calls in FastAPI
#import nest_asyncio
#   nest_asyncio.apply()


BASE_DIR = Path(__file__).resolve().parent


# =========================
# FastAPI Lifespan
# =========================

@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        # Initialize PostgreSQL and LangGraph
        await initialize_travel_graph()

        print("Application startup completed!")

        yield

    finally:
        # Close PostgreSQL connection
        await close_travel_graph()


app = FastAPI(
    title="TripMate AI",
    description="LangGraph Multi-Agent Travel Planner with FastAPI Frontend",
    version="1.0.0",
    lifespan=lifespan
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)



class TravelRequest(BaseModel):
    message: str
    thread_id: str | None = None



@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.post("/api/travel")
async def travel_planner(request_data: TravelRequest):
    try:
        user_message = request_data.message.strip()

        if not user_message:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Message cannot be empty."
                }
            )

        result = await run_travel_agent(
                    user_input=user_message,
                    thread_id=request_data.thread_id
                    )

        return JSONResponse(
            content={
                        "success": True,
                        "thread_id": result["thread_id"],
                        "answer": result["answer"],
                        "flight_results": result["flight_results"],
                        "hotel_results": result["hotel_results"],
                        "weather_results": result["weather_results"],
                        "itinerary": result["itinerary"],
                        "llm_calls": result["llm_calls"],
                    }
                )

    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )



@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "AI Travel Planner API is running"
    }


@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(content={})



if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )