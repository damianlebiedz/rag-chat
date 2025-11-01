from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from config import LLM
from llm_services.llm_chains import configure_qa_rag_chain, configure_llm_only_chain
from .api_models import Question

from langchain_neo4j import Neo4jGraph
from dotenv import load_dotenv

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from langchain.callbacks.base import BaseCallbackHandler
from queue import Queue
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware
import json

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
    if question.rag:
        output_function = configure_qa_rag_chain()

    q = Queue()

    def cb():
        output_function.invoke(question.text, config={"callbacks": [QueueCallback(q)]})

    def generate():
        yield json.dumps({"init": True, "model": LLM})
        for token, _ in stream(cb, q):
            yield json.dumps({"token": token})

    return EventSourceResponse(generate(), media_type="text/event-stream")
