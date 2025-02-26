import os

def create_project_structure(base_path="mystock_agents"):
    # Define the folder structure and files
    structure = {
        "agents": [
            "stock_agent.py",
            "recommendation_agent.py",
            "feedback_agent.py",
            "knowledge_worker_agent.py",
        ],
        "tools": [
            "data_fetcher.py",
            "sentiment_analysis.py",
            "news_scraper.py",
            "volume_analyzer.py",
            "technical_analysis.py",
            "performance_tracker.py",
            "feedback_optimizer.py",
            "alerts_manager.py",
            "logging_tool.py",
        ],
        "utils": [
            "config.py",
        ],
        "storage": [
            "recommendation_log.csv",
            "knowledge_retrieval_log.csv",
        ],
    }

    files_content = {
        "README.md": "# MyStock Agents\n\nThis project contains agents for stock analysis.",
        "requirements.txt": "",
        "main.py": "def main():\n    print('Starting MyStock Agents...')\n\nif __name__ == '__main__':\n    main()",
    }

    # Create base project folder
    os.makedirs(base_path, exist_ok=True)

    # Create directories and their respective files
    for folder, files in structure.items():
        folder_path = os.path.join(base_path, folder)
        os.makedirs(folder_path, exist_ok=True)
        for file in files:
            with open(os.path.join(folder_path, file), "w") as f:
                f.write("")  # Empty file

    # Create standalone files
    for file, content in files_content.items():
        with open(os.path.join(base_path, file), "w") as f:
            f.write(content)

    print(f"Project structure for '{base_path}' created successfully!")

# Run the script
create_project_structure()
