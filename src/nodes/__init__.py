"""LangGraph nodes for the Automated Auditor workflow."""

from src.nodes.detectives import DetectiveNodes, evidence_aggregator_node

__all__ = [
    "DetectiveNodes",
    "evidence_aggregator_node"
]