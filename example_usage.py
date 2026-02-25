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
        "pdf_path": "reports/interim_report.pdf",
        "rubric_dimensions": [
            {
                "id": "state_management_rigor",
                "name": "State Management Rigor",
                "target_artifact": "github_repo",
                "forensic_instruction": "Examine the repository for evidence of robust state management using Pydantic BaseModel or TypedDict"
            },
            {
                "id": "graph_orchestration_complexity",
                "name": "Graph Orchestration Complexity",
                "target_artifact": "github_repo",
                "forensic_instruction": "Analyze the graph structure for parallel execution patterns and complex state transitions"
            },
            {
                "id": "theoretical_depth",
                "name": "Theoretical Depth",
                "target_artifact": "pdf_report",
                "forensic_instruction": "Look for evidence of dialectical synthesis and fan-in/fan-out concepts in the document"
            }
        ],
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