import datetime
import sys
import os
from tools.neo4j_connector import retrieve_knowledge


# Add the "tools" and "utils" directories to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
tools_dir = os.path.join(current_dir, '..', 'tools')
utils_dir = os.path.join(current_dir, '..', 'utils')

sys.path.append(tools_dir)
sys.path.append(utils_dir)

# Print sys.path for debugging
print("Current sys.path:", sys.path)
# Check if the utils directory is correctly added to the path
print("utils directory exists:", os.path.exists(utils_dir))


# Import the module after ensuring the paths are correct

class KnowledgeWorkerAgent:
    def __init__(self):  # If you need initialization, add it here
        # Initialization code, if necessary (e.g., initializing Neo4j connection)
        pass

    def retrieve_knowledge(self, user_query):
        # Directly use the passed user_query instead of asking for input again
        response = retrieve_knowledge(user_query)

        if response:
            print("\n📚 Knowledge Retrieved:")
            if isinstance(response, list):
                for i, item in enumerate(response, 1):
                    print(f"  {i}. {item['name']}: {item['description']}")
            else:
                print(response)
        else:
            print("\n⚠️ No relevant knowledge found.")


if __name__ == "__main__":
    agent = KnowledgeWorkerAgent()
    agent.retrieve_knowledge("market factors")  # Pass query directly

