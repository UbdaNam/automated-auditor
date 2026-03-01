# Automated Auditor - Complete Digital Courtroom Implementation

A production-grade automated audit agent swarm built with LangGraph for forensic repository analysis.

## Architecture Overview

This implementation follows the "Digital Courtroom" architecture described in the TRP1 Challenge:

- **Layer 1: Detective Layer** - Forensic agents that collect objective evidence
- **Layer 2: Judicial Layer** - Three judge personas that interpret evidence dialectically
- **Layer 3: Chief Justice** - Deterministic synthesis engine for final verdict

## Implementation Status: Complete ✅

### Features Implemented

#### Core Infrastructure

- ✅ Typed state management using `Pydantic` and `TypedDict`
- ✅ Structured evidence collection with `Evidence` schema
- ✅ Parallel execution with fan-out/fan-in patterns
- ✅ Safe state reducers to prevent data overwrites

#### Forensic Tools (Layer 1)

- ✅ Sandboxed Git repository cloning and analysis
- ✅ AST-based Python code structure parsing
- ✅ PDF document analysis with Docling
- ✅ Cross-reference verification between code and documentation

#### LLM Detective Agents (Layer 1)

- ✅ `RepoInvestigatorAgent`: Code architecture and commit history analysis
- ✅ `DocAnalystAgent`: Documentation accuracy and concept depth analysis
- ✅ `VisionInspectorAgent`: Visual documentation analysis

#### Judicial Agents (Layer 2)

- ✅ `ProsecutorAgent`: Adversarial lens for finding flaws and security issues
- ✅ `DefenseAgent`: Benevolent lens for recognizing effort and intent
- ✅ `TechLeadAgent`: Pragmatic lens for architectural soundness

#### Graph Orchestration

- ✅ Parallel detective execution (fan-out)
- ✅ Evidence aggregation node (fan-in)
- ✅ Judicial parallel execution per rubric criterion
- ✅ Chief Justice deterministic synthesis
- ✅ Error handling and conditional routing
- ✅ Structured output enforcement

## Quick Start

### Prerequisites

1. Python 3.11+ installed
2. API keys for either:
   - Anthropic Claude (`ANTHROPIC_API_KEY`)
   - OpenAI GPT (`OPENAI_API_KEY`)

### Installation

```bash
# Clone the repository
git clone https://github.com/UbdaNam/automated-auditor.git
cd automated-auditor

# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Project Structure

```
src/
├── state.py              # Pydantic schemas and state management
├── graph.py              # LangGraph orchestration (Layers 1 + 2)
├── rubric.json           # Judicial constitution (10 dimensions)
├── nodes/
│   ├── detectives.py     # Detective node implementations
│   ├── judges.py         # Judicial nodes and parallel execution
│   └── justice.py        # Chief Justice synthesis engine
├── agents/
│   ├── detective_agents.py # LLM forensic agents
│   └── judge_agents.py   # Judicial persona agents
└── tools/
    ├── repo_tools.py     # Git and AST analysis
    └── doc_tools.py      # PDF analysis
```

## Forensic Protocols Implemented

### RepoInvestigator (Code Detective)

- ✅ Git history analysis for atomic vs bulk commits
- ✅ AST parsing for StateGraph instantiation verification
- ✅ Pydantic/TypedDict schema validation
- ✅ Parallel execution pattern detection

### DocAnalyst (Documentation Detective)

- ✅ Concept depth analysis vs buzzword usage
- ✅ Cross-reference validation between claims and code
- ✅ Hallucination detection for file references
- ✅ Theoretical understanding assessment

### VisionInspector (Visual Detective)

- ✅ Diagram pattern classification
- ✅ Parallel flow verification in visual documentation
- ✅ Architecture accuracy assessment

## Judicial Protocols Implemented

### Judge Personas (Layer 2)

```python
# Each judge evaluates independently with structured output
from src.agents.judge_agents import judge_agents

opinions = await judge_agents.evaluate_with_all_judges(
    criterion=criterion_data,
    evidence=collected_evidence
)

# Results in three distinct opinions:
# - prosecutor_opinion (critical perspective)
# - defense_opinion (benevolent perspective)
# - tech_lead_opinion (pragmatic perspective)
```

### Chief Justice Synthesis (Layer 3)

The Chief Justice applies deterministic rules:

1. **Security Override**: Security flaws cap scores at 3
2. **Fact Supremacy**: Evidence overrules judicial opinion
3. **Functionality Weight**: Tech Lead assessment carries highest weight
4. **Dissent Requirement**: High variance triggers explanation

### Rubric Integration

The system dynamically loads [`src/rubric.json`](src/rubric.json) containing:

- 10 comprehensive auditing criteria
- Success/failure patterns for each dimension
- Synthesis rules for conflict resolution

## Architecture Verification

The implementation includes validation against the full rubric specifications:

1. **Graph Orchestration**: Parallel fan-out/fan-in execution confirmed
2. **Structured Output**: All LLM calls use `.with_structured_output()`
3. **Dialectical Synthesis**: Three judge personas with deterministic resolution
4. **Dynamic Rubric Loading**: Supports arbitrary rubric dimensions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

## License

MIT License - See LICENSE file for details.

---

**Note**: This is not a complete implementation of the Digital Courtroom architecture. The system can audit arbitrary repositories against customizable rubrics with full forensic evidence collection and dialectical judicial synthesis.
