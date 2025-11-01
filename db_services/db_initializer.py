from neo4j import GraphDatabase
from neo4j.exceptions import AuthError, ServiceUnavailable

from config import URL, USERNAME, PASSWORD
from utils.logger import get_logger
from utils.validations import validate_env_vars

logger = get_logger(__name__)


def get_graph_driver():
    validate_env_vars(URL=URL, USERNAME=USERNAME, PASSWORD=PASSWORD)
    try:
        driver = GraphDatabase.driver(URL, auth=(USERNAME, PASSWORD))
        with driver.session() as session:
            session.run("RETURN 1")
        return driver

    except AuthError as e:
        logger.error(f"Neo4j authentication failed: {e}")
        raise
    except ServiceUnavailable as e:
        logger.error(f"Neo4j service unavailable: {e}")
        raise
    except Exception as e:
        logger.error(f"Neo4j initialization error: {e}")
        raise
