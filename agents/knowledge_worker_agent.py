import os
import sys
from tools.neo4j_connector import retrieve_knowledge

# Ensure paths are set correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
tools_dir = os.path.join(current_dir, "..", "tools")
utils_dir = os.path.join(current_dir, "..", "utils")

sys.path.append(tools_dir)
sys.path.append(utils_dir)


class KnowledgeWorkerAgent:
    def __init__(self):
        """Initialize Knowledge Worker Agent."""
        pass

    def retrieve_knowledge(self, user_query):
        """Retrieves knowledge from Neo4j and processes it for use."""
        response = retrieve_knowledge(user_query)

        if not response or isinstance(response, list) and not response[0]:
            print("\n⚠️ No relevant knowledge found.")
            return ["No relevant market knowledge available."]  # Ensure a non-empty list is returned

        processed_knowledge = []
        print("\n📚 Knowledge Retrieved:")
        for i, item in enumerate(response, 1):
            name = item.get("name", "Unknown")
            description = item.get("description", "No description available")
            print(f"  {i}. {name}: {description}")
            processed_knowledge.append(f"{name}: {description}")

        return processed_knowledge  # Ensure processed data is structured correctly


if __name__ == "__main__":
    agent = KnowledgeWorkerAgent()
    agent.retrieve_knowledge("market factors")
