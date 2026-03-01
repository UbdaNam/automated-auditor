"""
Complete Graph Orchestration for Automaton Auditor.
Includes Layer 1 (Detectives) and Layer 2 (Judicial Layer) integration.
"""

from typing import Literal, Dict, List, Hashable, Sequence
import json
from langgraph.graph import StateGraph, START, END

from src.state import AgentState
from src.nodes.detectives import DetectiveNodes, evidence_aggregator_node
from src.nodes.judges import judicial_nodes
from src.nodes.justice import chief_justice


def create_detective_graph() -> StateGraph:
    """Create the Layer 1 detective graph with parallel execution."""
    
    # Initialize detective nodes
    detective_nodes = DetectiveNodes()
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add detective nodes (parallel branches)
    workflow.add_node("repo_investigator", detective_nodes.repo_investigator_node)
    workflow.add_node("doc_analyst", detective_nodes.doc_analyst_node)
    # workflow.add_node("vision_inspector", detective_nodes.vision_inspector_node)  # Commented out - visual analysis unavailable
    
    # Add evidence aggregator node (fan-in point)
    workflow.add_node("evidence_aggregator", evidence_aggregator_node)
    
    # Define entry point routing
    def route_from_start(state: AgentState) -> Sequence[Hashable]:
        """Route from START to detectives in parallel."""
        print("[Router] Starting parallel detective execution...")
        
        # Check if repository and PDF are provided
        if not state.get("repo_url"):
            print("[Router] No repository URL provided")
            return ["evidence_aggregator"]
        
        if not state.get("pdf_path"):
            print("[Router] No PDF path provided")
            return ["repo_investigator"]
        
        # Start all detectives that have data to analyze
        routes = ["repo_investigator"]
        
        if state.get("pdf_path"):
            routes.append("doc_analyst")
            # routes.append("vision_inspector")  # Commented out - visual analysis unavailable
        
        return routes
    
    def route_after_aggregation(state: AgentState) -> str:
        """Route from aggregator based on completion status."""
        aggregated_evidence = state.get("aggregated_evidence")
        
        if aggregated_evidence:
            evidence_summary = aggregated_evidence.get("evidence_summary", {})
            required_sources = 2  # repo, doc detectives (vision inspector removed)
            
            # Allow completion even if some detectives failed
            collected_sources = evidence_summary.get("total_sources", 0)
            errors = evidence_summary.get("error_count", 0)
            
            print(f"[Router Debug] Collected sources: {collected_sources}, Errors: {errors}, Required: {required_sources}")
            
            if collected_sources + errors >= required_sources:
                print("[Router] Evidence aggregation complete, Layer 1 testing finished")
                return END
        
        print("[Router] Waiting for more evidence...")
        return "evidence_aggregator"  # Loop back for retry
    
    # Add edges from START (fan-out)
    workflow.add_conditional_edges(
        START,
        route_from_start,
        {
            "repo_investigator": "repo_investigator",
            "doc_analyst": "doc_analyst"
        }
    )
    
    # Add edges from detectives to aggregator
    workflow.add_edge("repo_investigator", "evidence_aggregator")
    workflow.add_edge("doc_analyst", "evidence_aggregator")
    # workflow.add_edge("vision_inspector", "evidence_aggregator")  # Commented out - visual analysis unavailable
    
    # Add conditional edge from aggregator
    workflow.add_conditional_edges(
        "evidence_aggregator",
        route_after_aggregation,
        {
            "context_builder": "context_builder",
            "evidence_aggregator": "evidence_aggregator"
        }
    )
    
    return workflow


def create_full_audit_graph() -> StateGraph:
    """Create the complete audit graph with Layers 1 and 2."""
    
    # Start with Layer 1
    workflow = create_detective_graph()
    
    # Add Layer 2 nodes
    workflow.add_node("context_builder", judicial_nodes.context_builder_node)
    workflow.add_node("opinion_aggregator", judicial_nodes.opinion_aggregator_node)
    workflow.add_node("chief_justice", chief_justice.chief_justice_node)
    
    def route_from_context_builder(state: AgentState) -> str:
        """Route from context builder."""
        rubric_dimensions = state.get("rubric_dimensions", [])
        
        if not rubric_dimensions:
            print("[Router] No rubric dimensions found, proceeding directly to Chief Justice")
            return "chief_justice"
        
        print(f"[Router] Routing {len(rubric_dimensions)} criteria for judicial processing")
        return "opinion_aggregator"
    
    def route_from_opinion_aggregator(state: AgentState) -> str:
        """Route based on opinion aggregation status."""
        status = state.get("judicial_aggregation_status", {})
        
        total_criteria = status.get("total_criteria", 0)
        complete_criteria = status.get("complete_criteria", 0)
        
        if complete_criteria >= total_criteria:
            print("[Router] All criteria processed, proceeding to Chief Justice")
            return "chief_justice"
        else:
            print(f"[Router] {complete_criteria}/{total_criteria} criteria processed")
            return "opinion_aggregator"
    
    def route_from_chief_justice(state: AgentState) -> str:
        """Route after Chief Justice synthesis."""
        if state.get("synthesis_complete", False):
            print("[Router] Synthesis complete, audit finished")
            return END
        return "chief_justice"
    
    # Add edges for Layer 2 flow
    workflow.add_edge("context_builder", "opinion_aggregator")
    workflow.add_edge("opinion_aggregator", "chief_justice")
    workflow.add_conditional_edges(
        "chief_justice",
        route_from_chief_justice,
        {
            END: END,
            "chief_justice": "chief_justice"
        }
    )
    
    return workflow


def compile_layer1_graph():
    """Compile only Layer 1 detective graph."""
    # Create a fresh workflow instead of modifying an existing one
    workflow = StateGraph(AgentState)
    
    # Initialize detective nodes
    detective_nodes = DetectiveNodes()
    
    # Add detective nodes (parallel branches)
    workflow.add_node("repo_investigator", detective_nodes.repo_investigator_node)
    workflow.add_node("doc_analyst", detective_nodes.doc_analyst_node)
    # workflow.add_node("vision_inspector", detective_nodes.vision_inspector_node)  # Commented out - visual analysis unavailable
    
    # Add evidence aggregator node (fan-in point)
    workflow.add_node("evidence_aggregator", evidence_aggregator_node)
    
    # Define entry point routing
    def route_from_start(state: AgentState) -> Sequence[Hashable]:
        """Route from START to all detectives in parallel."""
        print("[Router] Starting parallel detective execution...")
        
        # Check if repository and PDF are provided
        if not state.get("repo_url"):
            print("[Router] No repository URL provided")
            return ["evidence_aggregator"]
        
        if not state.get("pdf_path"):
            print("[Router] No PDF path provided")
            return ["repo_investigator", "evidence_aggregator"]
        
        # Start all detectives that have data to analyze
        routes = ["repo_investigator"]
        
        if state.get("pdf_path"):
            routes.append("doc_analyst")
            # routes.append("vision_inspector")  # Commented out - visual analysis unavailable
        
        return routes
    
    # Add edges from START (fan-out)
    workflow.add_conditional_edges(
        START,
        route_from_start,
        {
            "repo_investigator": "repo_investigator",
            "doc_analyst": "doc_analyst"
        }
    )
    
    # Add edges from detectives to aggregator
    workflow.add_edge("repo_investigator", "evidence_aggregator")
    workflow.add_edge("doc_analyst", "evidence_aggregator")
    # workflow.add_edge("vision_inspector", "evidence_aggregator")  # Commented out - visual analysis unavailable
    
    # Add conditional edge from aggregator that goes directly to END
    def route_after_aggregation_layer1(state: AgentState) -> str:
        """Route from aggregator directly to END for Layer 1."""
        aggregated_evidence = state.get("aggregated_evidence")
        
        if aggregated_evidence and aggregated_evidence.get("evidence_summary", {}).get("total_sources", 0) > 0:
            print("[Router] Layer 1 complete, proceeding to END")
            return END
        print("[Router] Waiting for more evidence...")
        return "evidence_aggregator"  # Loop back for retry
    
    workflow.add_conditional_edges(
        "evidence_aggregator",
        route_after_aggregation_layer1,
        {
            END: END,
            "evidence_aggregator": "evidence_aggregator"
        }
    )
    
    graph = workflow.compile()
    print("[Graph] Layer 1 Detective Graph compiled successfully")
    print("[Graph] Architecture: START → Detectives (Parallel) → EvidenceAggregator → END")
    return graph


def compile_full_graph():
    """Compile the complete audit graph with both layers."""
    workflow = create_full_audit_graph()
    graph = workflow.compile()
    
    print("[Graph] Complete Audit Graph compiled successfully")
    print("[Graph] Architecture: START → Detectives (Parallel) → EvidenceAggregator")
    print("[Graph]          → ContextBuilder → OpinionAggregator → ChiefJustice → END")
    
    return graph


def run_audit_analysis(repo_url: str, pdf_path: str = "", rubric_file: str = "src/rubric.json") -> dict:
    """Run complete audit analysis with Layers 1 and 2."""
    
    # Load rubric dimensions
    try:
        with open(rubric_file, 'r') as f:
            rubric_data = json.load(f)
        rubric_dimensions = rubric_data.get("dimensions", [])
    except Exception as e:
        print(f"[Graph] Error loading rubric: {e}")
        rubric_dimensions = []
    
    # Initialize state
    initial_state = AgentState(
        repo_url=repo_url,
        pdf_path=pdf_path,
        rubric_dimensions=rubric_dimensions,
        evidences={},
        opinions=[],
        final_report=None,
        error=None,
        error_context=None
    )
    
    # Compile graph
    graph = compile_full_graph()
    
    try:
        # Execute the graph
        result = graph.invoke(initial_state)
        
        print("[Graph] Complete audit analysis completed successfully")
        return {
            "success": True,
            "state": result,
            "final_report": result.get("final_report", None)
        }
        
    except Exception as e:
        print(f"[Graph] Analysis failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "state": initial_state
        }


def run_detective_analysis_only(repo_url: str, pdf_path: str = "") -> dict:
    """Run only Layer 1 detective analysis (for testing)."""
    
    # Initialize state
    initial_state = AgentState(
        repo_url=repo_url,
        pdf_path=pdf_path,
        rubric_dimensions=[],
        evidences={},
        opinions=[],
        final_report=None,
        error=None,
        error_context=None
    )
    
    # Compile Layer 1 graph
    graph = compile_layer1_graph()
    
    try:
        # Execute the graph
        result = graph.invoke(initial_state)
        
        print("[Graph] Detective analysis completed successfully")
        return {
            "success": True,
            "state": result,
            "evidence_summary": result.get("aggregated_evidence", {})
        }
        
    except Exception as e:
        print(f"[Graph] Analysis failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "state": initial_state
        }


if __name__ == "__main__":
    """Test the audit graph with sample data."""
    
    # Sample test
    test_repo = "https://github.com/UbdaNam/automated-auditor.git"
    test_pdf = "./reports/interim_report.pdf"
    
    print("=== Complete Audit Graph Test ===")
    result = run_audit_analysis(test_repo, test_pdf)
    
    if result["success"]:
        print("Test completed successfully!")
        final_report = result["final_report"]
        if final_report:
            print(f"Overall Score: {final_report.get('overall_score', 'N/A')}")
    else:
        print(f"Test failed: {result['error']}")