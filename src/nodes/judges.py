"""
Judicial Layer Nodes - Parallel execution of judge evaluation per criterion.
"""

import json
from typing import Dict, List, Any
from langgraph.graph import StateGraph

from src.state import AgentState, JudicialOpinion
from src.agents.judge_agents import judge_agents


class JudicialNodes:
    """Nodes for judicial layer processing."""
    
    def __init__(self):
        self.judge_agents = judge_agents
    
    async def context_builder_node(self, state: AgentState) -> Dict[str, Any]:
        """Build context for judicial layer by loading and filtering rubric."""
        
        print("[Judicial] Building context from aggregated evidence...")
        
        # Load rubric dimensions from state
        rubric_dimensions = state.get("rubric_dimensions", [])
        evidences = state.get("evidences", {})
        
        # Build judicial contexts
        judicial_contexts = {}
        
        for dimension in rubric_dimensions:
            dimension_id = dimension["id"]
            
            # Get relevant evidence for this criterion
            criterion_evidence = self._get_evidence_for_criterion(evidences, dimension_id)
            
            judicial_contexts[dimension_id] = {
                "dimension": dimension,
                "evidence": criterion_evidence,
                "target_artifact": dimension.get("target_artifact", "github_repo"),
                "forensic_instruction": dimension.get("forensic_instruction", ""),
                "judicial_details": f"Criterion: {dimension['name']}\n"
                                   f"ID: {dimension['id']}\n"
                                   f"Target: {dimension.get('target_artifact', 'github_repo')}"
            }
        
        # Add synthesis rules
        judicial_contexts["synthesis_rules"] = {
            "security_override": "Confirmed security flaws cap score at 3",
            "fact_supremacy": "Forensic evidence overrules judicial opinion",
            "functionality_weight": "Tech Lead architecture assessment carries high weight",
            "dissent_requirement": "Score variance > 2 requires dissent explanation",
            "variance_re_evaluation": "High variance triggers evidence re-evaluation"
        }
        
        return {
            "judicial_contexts": judicial_contexts,
            **state
        }
    
    def _get_evidence_for_criterion(self, evidences: Dict[str, List], criterion_id: str) -> str:
        """Extract evidence relevant to a specific criterion."""
        evidence_list = []
        
        # Look for evidence that matches this criterion's goals
        for goal, evidence_items in evidences.items():
            if criterion_id in goal.lower() or goal.lower() in criterion_id.lower():
                for evidence in evidence_items:
                    if evidence.get("found", False):
                        evidence_list.append(
                            f"Goal: {evidence.get('goal', 'Unknown')}\n"
                            f"Location: {evidence.get('location', 'Unknown')}\n"
                            f"Rationale: {evidence.get('rationale', '')}\n"
                        )
        
        # If no direct match, use general evidence
        if not evidence_list:
            evidence_list = [
                f"Evidence summary from {len(evidences)} goals collected"
            ]
        
        return "\n---\n".join(evidence_list[:5])  # Limit to top 5 pieces of evidence
    
    def process_criterion_node(self, state: AgentState, criterion_id: str) -> Dict[str, Any]:
        """Process a single criterion through all three judges."""
        
        print(f"[Judicial] Processing criterion: {criterion_id}")
        
        # Get context for this criterion
        judicial_contexts = state.get("judicial_contexts", {})
        criterion_context = judicial_contexts.get(criterion_id, {})
        
        dimension = criterion_context.get("dimension", {})
        evidence = criterion_context.get("evidence", "")
        
        if not dimension:
            print(f"[Judicial] Warning: No context found for criterion {criterion_id}")
            return state
        
        try:
            # Evaluate with all three judges
            import asyncio
            opinions = asyncio.run(judge_agents.evaluate_with_all_judges(dimension, evidence))
            
            # Add opinions to state using the 'operator.add' reducer
            current_opinions = state.get("opinions", [])
            return {
                **state,
                "opinions": current_opinions + opinions,
                f"{criterion_id}_processed": True
            }
            
        except Exception as e:
            print(f"[Judicial] Error processing criterion {criterion_id}: {e}")
            # Add error opinions as fallback
            error_opinion = JudicialOpinion(
                judge="Prosecutor",
                criterion_id=criterion_id,
                score=3,
                argument=f"Evaluation failed: {str(e)}",
                cited_evidence=[]
            )
            
            current_opinions = state.get("opinions", [])
            return {
                **state,
                "opinions": current_opinions + [error_opinion] * 3,  # Add three identical opinions
                "error": f"Criterion {criterion_id} processing failed",
                "error_context": str(e)
            }
    
    def opinion_aggregator_node(self, state: AgentState) -> Dict[str, Any]:
        """Aggregate opinions across all criteria."""
        
        print("[Judicial] Aggregating judge opinions...")
        
        opinions = state.get("opinions", [])
        rubric_dimensions = state.get("rubric_dimensions", [])
        
        # Group opinions by criterion
        opinions_by_criterion = {}
        for opinion in opinions:
            criterion_id = opinion.criterion_id
            if criterion_id not in opinions_by_criterion:
                opinions_by_criterion[criterion_id] = []
            opinions_by_criterion[criterion_id].append(opinion)
        
        # Check completion status
        expected_criteria = set([dim["id"] for dim in rubric_dimensions])
        processed_criteria = set(opinions_by_criterion.keys())
        
        # Each criterion should have 3 opinions (one from each judge)
        complete_criteria = {
            cid for cid, ops in opinions_by_criterion.items()
            if len(ops) >= 3
        }
        
        completion_status = {
            "total_criteria": len(expected_criteria),
            "processed_criteria": len(processed_criteria),
            "complete_criteria": len(complete_criteria),
            "expected_criteria": list(expected_criteria),
            "criteria_status": {
                cid: len(opinions_by_criterion.get(cid, [])) for cid in expected_criteria
            }
        }
        
        return {
            **state,
            "opinions_by_criterion": opinions_by_criterion,
            "judicial_aggregation_status": completion_status
        }

    def _process_criterion_wrapper(self, state: AgentState, criterion_id: str) -> Dict[str, Any]:
        """Wrapper for criterion processing."""
        return self.process_criterion_node(state, criterion_id)


def create_judicial_graph(judges: JudicialNodes) -> StateGraph:
    """Create the judicial layer graph for criterion parallel processing."""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("context_builder", judges.context_builder_node)
    workflow.add_node("opinion_aggregator", judges.opinion_aggregator_node)
    
    # Add criterion nodes dynamically
    rubric_dimensions = []  # Will be loaded from state
    
    def route_from_context_builder(state: AgentState) -> List[str]:
        """Route to criterion nodes based on rubric dimensions."""
        
        rubric_dimensions = state.get("rubric_dimensions", [])
        criterion_ids = [dim["id"] for dim in rubric_dimensions]
        
        # Create nodes for each criterion
        for cid in criterion_ids:
            node_name = f"criterion_{cid}"
            # Add node unconditionally since we're building dynamically
            workflow.add_node(node_name, lambda s, cid=cid: judges._process_criterion_wrapper(s, cid))
        
        # Route to all criterion nodes in parallel
        routes = {node_name: node_name for node_name in [f"criterion_{cid}" for cid in criterion_ids]}
        routes["opinion_aggregator"] = "opinion_aggregator"  # Also route directly for safety
        
        return list(routes.keys())
    
    def check_aggregation_complete(state: AgentState) -> str:
        """Check if all opinions have been aggregated."""
        status = state.get("judicial_aggregation_status", {})
        
        total = status.get("total_criteria", 0)
        complete = status.get("complete_criteria", 0)
        
        if complete >= total:
            return "chief_justice"
        elif complete > 0:
            return "opinion_aggregator"  # Wait for remaining criteria
        else:
            return "opinion_aggregator"  # Initial state
    
    # Define edges
    workflow.add_edge("context_builder", "opinion_aggregator")
    
    # Conditional edge from context builder to start parallel processing
    workflow.add_conditional_edges(
        "context_builder",
        route_from_context_builder
    )
    
    # Edge from criterion nodes back to aggregator
    workflow.add_edge("opinion_aggregator", "judicial_complete_checker")
    
    # Add final completion checker node
    workflow.add_node("judicial_complete_checker", lambda state: state)
    workflow.add_conditional_edges(
        "judicial_complete_checker",
        check_aggregation_complete,
        {
            "chief_justice": "chief_justice",
            "opinion_aggregator": "opinion_aggregator"
        }
    )
    
    return workflow


# Convenience instance
judicial_nodes = JudicialNodes()