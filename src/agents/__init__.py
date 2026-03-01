"""LLM Detective Agents for forensic analysis."""

from src.agents.detective_agents import (
    RepoInvestigatorAgent,
    DocAnalystAgent,
    VisionInspectorAgent
)

__all__ = [
    "RepoInvestigatorAgent",
    "DocAnalystAgent",
    "VisionInspectorAgent"
]