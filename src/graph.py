from typing import Dict, List
from langgraph.graph import StateGraph, END
from .state import AgentState, Evidence
from .nodes.detectives import RepoInvestigator, DocAnalyst

def create_detective_graph():
    """Create the initial graph with detective nodes."""
    
    # Initialize detectives
    repo_investigator = RepoInvestigator()
    doc_analyst = DocAnalyst()
    
    # Define graph
    workflow = StateGraph(AgentState)
    
    # Define nodes
    def investigate_repository(state: AgentState):
        """Investigate the target repository using rubric guidance."""
        print(f"Investigating repository: {state['repo_url']}")
        evidences = repo_investigator.investigate_codebase(state["repo_url"], state.get("rubric_dimensions", []))
        return {"evidences": evidences}
    
    def analyze_document(state: AgentState):
        """Analyze the accompanying document using rubric guidance."""
        print(f"Analyzing document: {state['pdf_path']}")
        evidences = doc_analyst.analyze_document(state["pdf_path"], state.get("rubric_dimensions", []))
        return {"evidences": evidences}
    
    def aggregate_evidence(state: AgentState):
        """Aggregate evidence from all detectives."""
        # This is a placeholder for evidence aggregation
        print("Aggregating evidence from all detectives")
        # Merge all evidence collections
        aggregated_evidences = state.get("evidences", {})
        return {"evidences": aggregated_evidences}
    
    # Add nodes to graph
    workflow.add_node("investigate_repository", investigate_repository)
    workflow.add_node("analyze_document", analyze_document)
    workflow.add_node("aggregate_evidence", aggregate_evidence)
    
    # Set entry point
    workflow.set_entry_point("investigate_repository")
    
    # Add edges
    workflow.add_edge("investigate_repository", "analyze_document")
    workflow.add_edge("analyze_document", "aggregate_evidence")
    workflow.add_edge("aggregate_evidence", END)
    
    return workflow.compile()

# Create the graph
try:
    detective_graph = create_detective_graph()
    print("Detective graph created successfully!")
except Exception as e:
    print(f"Failed to create detective graph: {e}")
    detective_graph = None
