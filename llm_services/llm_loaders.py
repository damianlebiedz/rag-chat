from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama

from utils.logger import get_logger
from config import OLLAMA_BASE_URL, LLM

logger = get_logger(__name__)


def load_embedding_model():
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        cache_folder="./embedding_model",
    )
    dimension = 384
    logger.info("Using sentence-transformers")

    return embeddings, dimension


def load_llm():
    logger.info(f"Using {LLM}")
    return ChatOllama(
        temperature=0.8,
        base_url=OLLAMA_BASE_URL,
        model=LLM,
        top_k=40,
        top_p=0.9,
    )
