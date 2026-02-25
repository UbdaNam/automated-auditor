import os
from dotenv import load_dotenv
from src.graph import create_detective_graph
from src.state import AgentState

# Load environment variables
load_dotenv()

def main():
    """Run the detective graph with a sample repository."""
    # Create the graph
    try:
        detective_graph = create_detective_graph()
        print("✓ Detective graph created successfully")
    except Exception as e:
        print(f"✗ Failed to create detective graph: {e}")
        return
    
    # Create initial state using the proper AgentState type
    initial_state: AgentState = {
        "repo_url": "https://github.com/UbdaNam/automated-auditor.git",
        "pdf_path": "reports/interim_report.md",  # Using our own report as example
        "rubric_dimensions": [],
        "evidences": {},
        "opinions": [],
        "final_report": None
    }
    
    print("✓ Initial state created successfully")
    print("Starting graph execution...")
    
    # Try to run the graph
    try:
        result = detective_graph.invoke(initial_state)
        print("✓ Graph execution completed successfully")
        print(f"Result keys: {result.keys()}")
    except Exception as e:
        print(f"✗ Graph execution failed: {e}")

if __name__ == "__main__":
    main()