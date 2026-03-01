"""Automated Auditor - Complete Digital Courtroom Implementation."""

# Import core components for easy access
from .state import (
    Evidence,
    JudicialOpinion,
    CriterionResult,
    AuditReport,
    AgentState
)
from .graph import (
    compile_layer1_graph,
    compile_full_graph,
    run_detective_analysis_only,
    run_audit_analysis
)

__version__ = "0.1.0"
__author__ = "Automated Auditor Team"

__all__ = [
    "Evidence",
    "JudicialOpinion", 
    "CriterionResult",
    "AuditReport",
    "AgentState",
    "compile_layer1_graph",
    "compile_full_graph",
    "run_detective_analysis_only",
    "run_audit_analysis"
]