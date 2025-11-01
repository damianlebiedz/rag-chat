from config import LLM
from llm_services.llm_chains import configure_llm_only_chain
from .api_models import Question

from fastapi import FastAPI, Depends
from queue import Queue
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import uvicorn

from .api_utils import stream, QueueCallback

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/query-stream")
def qstream(question: Question = Depends()):
    output_function = configure_llm_only_chain()

    q = Queue()

    def cb():
        output_function.invoke(question.text, config={"callbacks": [QueueCallback(q)]})

    def generate():
        yield json.dumps({"init": True, "model": LLM})
        for token, _ in stream(cb, q):
            yield json.dumps({"token": token})

    return EventSourceResponse(generate(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8504,
        reload=True
    )
