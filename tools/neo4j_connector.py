import sys
import os

# Ensure the parent directory is added to the sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # This is Stock_Graph_Master
sys.path.append(parent_dir)

from neo4j import GraphDatabase
from utils.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

class Neo4jConnector:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def run_query(self, query, params=None):
        """Executes a parameterized Neo4j query and returns results."""
        with self.driver.session() as session:
            result = session.run(query, params)
            return result.data()

def retrieve_knowledge(user_query):
    """Retrieves knowledge from Neo4j based on user input keywords."""
    connector = Neo4jConnector()

    # Extract keywords (for now, split by space)
    keywords = user_query.lower().split()

    # Cypher query to match relevant nodes based on keywords
    cypher_query = """
    MATCH (n)
    WHERE ANY(keyword IN $keywords WHERE toLower(n.name) CONTAINS keyword OR toLower(n.description) CONTAINS keyword)
    RETURN n.name AS name, n.description AS description LIMIT 5
    """

    result = connector.run_query(cypher_query, {"keywords": keywords})
    connector.close()

    return result if result else "No relevant knowledge found."
