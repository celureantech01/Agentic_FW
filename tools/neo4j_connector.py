import sys
import os
from neo4j import GraphDatabase
from utils.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

# Ensure the parent directory is added to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # This is Stock_Graph_Master
sys.path.append(parent_dir)

class Neo4jConnector:
    def __init__(self):
        """Initializes Neo4j connection with error handling."""
        try:
            self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        except Exception as e:
            print(f"Error connecting to Neo4j: {e}")
            self.driver = None  # Prevents further execution if connection fails

    def close(self):
        """Closes the Neo4j connection."""
        if self.driver:
            self.driver.close()

    def run_query(self, query, params=None):
        """Executes a Neo4j query with parameters and returns results."""
        if not self.driver:
            return []  # Return empty list if connection failed

        with self.driver.session() as session:
            result = session.run(query, params)
            return result.data()

def retrieve_knowledge(user_query):
    """Retrieves knowledge from Neo4j based on extracted keywords."""
    connector = Neo4jConnector()
    if not connector.driver:
        return ["No relevant knowledge found (Neo4j connection issue)."]

    # Extract keywords (splitting user query into words)
    keywords = user_query.lower().split()

    # Cypher query to find relevant knowledge
    cypher_query = """
    MATCH (n)
    WHERE ANY(keyword IN $keywords WHERE 
        toLower(COALESCE(n.name, '')) CONTAINS keyword OR 
        toLower(COALESCE(n.description, '')) CONTAINS keyword)
    RETURN COALESCE(n.name, 'Unknown') AS name, COALESCE(n.description, 'No description available') AS description
    LIMIT 5
    """

    result = connector.run_query(cypher_query, {"keywords": keywords})
    connector.close()

    return result if result else ["No relevant knowledge found."]
