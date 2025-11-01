import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
IS_DOCKER = bool(os.getenv("DOCKER_ENV"))

if not IS_DOCKER:
    os.environ.update({
        "NEO4J_HOST": "localhost",
        "OLLAMA_HOST": "localhost",
    })

# LLM
LLM = os.getenv("LLM")

# Neo4j
NEO4J_HOST = os.getenv("NEO4J_HOST")
NEO4J_PORT = os.getenv("NEO4J_PORT")
URL = f"neo4j://{NEO4J_HOST}:{NEO4J_PORT}"

USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

# Ollama
OLLAMA_HOST = os.getenv("OLLAMA_HOST")
OLLAMA_PORT = os.getenv("OLLAMA_PORT")
OLLAMA_BASE_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
