from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
import logging
from dotenv import load_dotenv

# Import our verbose generator
# We need to make sure the root dir is in python path or install the package
# For this script we assume running from root
from thinking_budget.verbose.logic import run_single_question_verbose

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/stream")
async def stream_process(question: str, importance: str = "normal"):
    """
    SSE Endpoint that streams the thinking process steps.
    """
    async def event_generator():
        try:
            # We iterate over the synchronous generator
            # In a real heavy app we might offload to threadpool but this is a POC
            for event in run_single_question_verbose(question, importance):
                yield {
                    "event": "update",
                    "data": json.dumps(event)
                }
                # Yield control to event loop to allow flushing
                await asyncio.sleep(0.01)
        except Exception as e:
            logging.error(f"Error during streaming: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)})
            }

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
