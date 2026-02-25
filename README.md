# Automated Auditor

An AI-powered system for auditing AI-generated code repositories using a digital courtroom metaphor with specialized detective, judge, and chief justice agents.

## Features

- **RepoInvestigator**: Analyzes repository structure, git history, and code artifacts
- **DocAnalyst**: Examines accompanying documentation for theoretical depth
- **VisionInspector**: (Planned) Analyzes architectural diagrams
- **Judicial Layer**: Evaluates evidence through different perspectives
- **Chief Justice**: Synthesizes final verdict with remediation plans

## Features Implemented

- ✅ Strongly-typed state definitions using Pydantic models
- ✅ Secure forensic tools for repository and document analysis
- ✅ Detective agents (RepoInvestigator and DocAnalyst) that collect structured evidence
- ✅ Initial LangGraph wiring for parallel execution
- ✅ Dependency management with pyproject.toml
- ✅ Environment configuration template

## Installation

1. Install dependencies using uv:

   ```bash
   pip install uv
   uv sync
   ```

2. Copy `.env.example` to `.env` and fill in your API keys:

   ```bash
   cp .env.example .env
   ```

3. Install additional system dependencies:
   - Git command-line tools
   - Python 3.9+

## Usage

To run the detective graph against a repository:

```python
from src.graph import detective_graph

# Define initial state
initial_state = {
    "repo_url": "https://github.com/example/target-repo.git",
    "pdf_path": "path/to/report.pdf",
    "rubric_dimensions": [],  # Will be populated from rubric
    "evidences": {},
    "opinions": [],
    "final_report": None
}

# Execute the graph
result = detective_graph.invoke(initial_state)
print(result)
```

## Project Structure

```
automated-auditor/
├── src/
│   ├── state.py              # Pydantic models and state definitions
│   ├── tools/                # Forensic analysis tools
│   │   ├── repo_tools.py     # Repository analysis functions
│   │   └── doc_tools.py      # Document analysis functions
│   ├── nodes/                # LangGraph nodes
│   │   └── detectives.py     # Detective agent implementations
│   └── graph.py              # LangGraph workflow definition
├── pyproject.toml            # Dependencies and metadata
├── .env.example             # Environment variable template
└── README.md                # This file
```

## Components

### State Definitions (src/state.py)

Defines the Pydantic models used throughout the system:

- `Evidence`: Structured data collected by detectives
- `JudicialOpinion`: Opinions from different judge personas
- `AuditReport`: Final audit report structure
- `AgentState`: Main state object for the LangGraph

### Forensic Tools (src/tools/)

Contains tools for analyzing repositories and documents:

- `repo_tools.py`: Git operations, AST analysis, file discovery
- `doc_tools.py`: PDF parsing, content querying, concept extraction

### Detective Nodes (src/nodes/detectives.py)

Implementation of the detective agents:

- `RepoInvestigator`: Analyzes repository structure and code artifacts
- `DocAnalyst`: Examines documentation for theoretical depth

### Graph Wiring (src/graph.py)

LangGraph implementation connecting the detective nodes in a workflow.

## Development

This project uses:

- `uv` for dependency management
- LangSmith for tracing

## Future Implementation

- VisionInspector implementation
- Judicial layer with Prosecutor, Defense, and Tech Lead personas
- ChiefJusticeNode with deterministic conflict resolution rules
- Complete StateGraph with parallel fan-out/fan-in for both detectives and judges
- Dockerfile for containerized runtime
- Full audit reports generation
