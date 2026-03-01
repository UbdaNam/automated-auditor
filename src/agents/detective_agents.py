import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from src.state import Evidence


# Load environment variables
load_dotenv()


class DetectiveAgentBase:
    """Base class for detective agents with common functionality."""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LLM with fallback logic."""
        # Use OpenAI GPT models
        if os.getenv("OPENAI_API_KEY"):
            return ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1
            )
        else:
            raise ValueError("No API key found. Set OPENAI_API_KEY")
    
    def _create_structured_prompt(self, system_prompt: str) -> ChatPromptTemplate:
        """Create a structured prompt template."""
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", """
            Analyze the following forensic data and provide structured evidence:
            
            {forensic_data}
            
            Respond with JSON matching the Evidence schema:
            goal: string (what were you investigating)
            found: boolean (did you find what you were looking for)
            content: string (details of what you found)
            location: string (where it was found)
            rationale: string (your reasoning)
            confidence: float (0.0 to 1.0)
            """)
        ])


class RepoInvestigatorAgent(DetectiveAgentBase):
    """Agent for analyzing code repositories and architectural patterns."""
    
    def __init__(self):
        super().__init__("RepoInvestigator")
        self.system_prompt = """You are a forensic code detective specializing in repository analysis. 
        Your role is to objectively analyze code structure, architectural patterns, and development history.
        
        Forensic Protocols:
        1. STATE STRUCTURE: Look for typed state definitions (Pydantic BaseModel, TypedDict)
        2. GRAPH WIRING: Verify LangGraph StateGraph instantiation and parallel execution patterns
        3. GIT NARRATIVE: Analyze commit history for atomic vs monolithic patterns
        4. SAFETY CHECKS: Verify sandboxing and error handling
        
        Be meticulous and objective. Only report what you can verify through forensic analysis.
        Do not speculate or make assumptions about intent.
        """
    
    def analyze_repository(self, forensic_data: Dict) -> Evidence:
        """Analyze repository forensic data and produce evidence."""
        prompt = self._create_structured_prompt(self.system_prompt)
        
        # Convert forensic data to string format for the prompt
        forensic_str = self._format_forensic_data(forensic_data)
        
        # Create chain with structured output
        chain = prompt | self.llm | JsonOutputParser(pydantic_object=Evidence)
        
        try:
            evidence = chain.invoke({"forensic_data": forensic_str})
            return evidence
        except Exception as e:
            # Fallback to manual parsing
            return Evidence(
                goal="Analyze repository structure",
                found=False,
                content=f"Analysis failed: {e}",
                location="repository_root",
                rationale="LLM analysis failed",
                confidence=0.1
            )
    
    def _format_forensic_data(self, data: Dict) -> str:
        """Format forensic data for the LLM prompt."""
        formatted = []
        
        if "git_analysis" in data:
            git_data = data["git_analysis"]
            formatted.append("GIT HISTORY ANALYSIS:")
            formatted.append(f"- Total commits: {git_data.get('total_commits', 0)}")
            formatted.append(f"- Bulk upload pattern: {git_data.get('has_bulk_upload', False)}")
            formatted.append(f"- Progression pattern: {git_data.get('has_progression', False)}")
            formatted.append(f"- Atomic commits: {git_data.get('is_atomic', False)}")
            
            commits = git_data.get("commit_timeline", [])
            formatted.append(f"- First 3 commits: {[c.get('message', '')[:50] for c in commits[:3]]}")
        
        if "ast_analysis" in data:
            ast_data = data["ast_analysis"]
            formatted.append("\nAST ANALYSIS:")
            formatted.append(f"- StateGraph found: {ast_data.get('has_state_graph', False)}")
            formatted.append(f"- Parallel wiring: {ast_data.get('has_parallel_wiring', False)}")
            
            classes = ast_data.get("classes", [])
            pydantic_classes = [c["name"] for c in classes if c.get("has_pydantic", False)]
            formatted.append(f"- Pydantic classes: {pydantic_classes}")
        
        if "file_structure" in data:
            fs_data = data["file_structure"]
            formatted.append("\nFILE STRUCTURE:")
            formatted.append(f"- Python files: {len(fs_data.get('python_files', []))}")
            formatted.append(f"- Has src/state.py: {'src/state.py' in str(fs_data.get('python_files', []))}")
            formatted.append(f"- Has src/graph.py: {'src/graph.py' in str(fs_data.get('python_files', []))}")
        
        return "\n".join(formatted)


class DocAnalystAgent(DetectiveAgentBase):
    """Agent for analyzing documentation and cross-referencing claims."""
    
    def __init__(self):
        super().__init__("DocAnalyst")
        self.system_prompt = """You are a forensic documentation analyst specializing in verifying claims 
        against actual code evidence. Your role is to detect hallucination and verify accuracy.
        
        Forensic Protocols:
        1. CITATION CHECK: Verify all file/feature claims against code evidence
        2. CONCEPT DEPTH: Analyze theoretical understanding vs buzzword usage
        3. CROSS-REFERENCE: Compare documentation claims with repository reality
        4. HALLUCINATION DETECTION: Flag unsubstantiated claims
        
        Be skeptical and thorough. When claims don't match evidence, document it clearly.
        Distinguish between facts (verifiable) and assertions (unverified).
        """
    
    def analyze_documentation(self, forensic_data: Dict) -> Evidence:
        """Analyze documentation forensic data and produce evidence."""
        prompt = self._create_structured_prompt(self.system_prompt)
        
        forensic_str = self._format_forensic_data(forensic_data)
        
        chain = prompt | self.llm | JsonOutputParser(pydantic_object=Evidence)
        
        try:
            evidence = chain.invoke({"forensic_data": forensic_str})
            return evidence
        except Exception as e:
            return Evidence(
                goal="Analyze documentation accuracy",
                found=False,
                content=f"Analysis failed: {e}",
                location="documentation",
                rationale="LLM analysis failed",
                confidence=0.1
            )
    
    def _format_forensic_data(self, data: Dict) -> str:
        """Format documentation forensic data."""
        formatted = []
        
        if "content_analysis" in data:
            content_data = data["content_analysis"]
            formatted.append("DOCUMENTATION CONTENT:")
            formatted.append(f"- Length: {content_data.get('length', 0)} characters")
            formatted.append(f"- Pages estimated: {content_data.get('pages', 0)}")
            formatted.append(f"- Successfully extracted: {content_data.get('success', False)}")
        
        if "concept_analysis" in data:
            concept_data = data["concept_analysis"]
            formatted.append("\nCONCEPT ANALYSIS:")
            for concept, analysis in concept_data.items():
                formatted.append(f"- {concept}: {analysis.get('occurrences', 0)} occurrences")
                formatted.append(f"  Deep explanations: {analysis.get('has_deep_explanation', False)}")
                formatted.append(f"  Buzzword usage: {analysis.get('is_buzzword', False)}")
        
        if "cross_reference" in data:
            cross_data = data["cross_reference"]
            formatted.append("\nCROSS-REFERENCE ANALYSIS:")
            formatted.append(f"- Files mentioned: {len(cross_data.get('mentioned_files', []))}")
            formatted.append(f"- Files verified: {len(cross_data.get('verified_files', []))}")
            formatted.append(f"- Files hallucinated: {len(cross_data.get('hallucinated_files', []))}")
            formatted.append(f"- Hallucination rate: {cross_data.get('hallucination_rate', 1.0):.2f}")
        
        return "\n".join(formatted)


class VisionInspectorAgent(DetectiveAgentBase):
    """Agent for analyzing architectural diagrams and visual evidence."""
    
    def __init__(self):
        super().__init__("VisionInspector")
        self.system_prompt = """You are a forensic visual analyst specializing in architectural diagrams 
        and visual evidence. Your role is to verify diagram accuracy against claimed architecture.
        
        Forensic Protocols:
        1. FLOW ANALYSIS: Verify parallel execution patterns
        2. TYPE CLASSIFICATION: Categorize diagram types (StateGraph, sequence, flowchart)
        3. ACCURACY VERIFICATION: Compare diagram flow with code implementation
        4. MISLEADING DETECTION: Flag misleading or generic diagrams
        
        Focus on structural accuracy. Diagrams should clearly show parallel execution paths
        (Detectives → Evidence Aggregation → Judges → Synthesis).
        """
    
    def analyze_visuals(self, forensic_data: Dict) -> Evidence:
        """Analyze visual forensic data and produce evidence."""
        prompt = self._create_structured_prompt(self.system_prompt)
        
        forensic_str = self._format_forensic_data(forensic_data)
        
        chain = prompt | self.llm | JsonOutputParser(pydantic_object=Evidence)
        
        try:
            evidence = chain.invoke({"forensic_data": forensic_str})
            return evidence
        except Exception as e:
            return Evidence(
                goal="Analyze visual documentation",
                found=False,
                content=f"Analysis failed: {e}",
                location="visual_content",
                rationale="LLM analysis failed",
                confidence=0.1
            )
    
    def _format_forensic_data(self, data: Dict) -> str:
        """Format visual forensic data."""
        formatted = []
        
        formatted.append("VISUAL ANALYSIS DATA:")
        
        if "image_analysis" in data:
            img_data = data["image_analysis"]
            formatted.append(f"- Image references found: {img_data.get('total_references', 0)}")
            formatted.append(f"- Specific references: {img_data.get('image_references', [])}")
        
        if "diagram_content" in data:
            diagram_data = data["diagram_content"]
            formatted.append(f"- Diagram type: {diagram_data.get('type', 'unknown')}")
            formatted.append(f"- Shows parallel flow: {diagram_data.get('has_parallel_flow', False)}")
            formatted.append(f"- Accurate architecture: {diagram_data.get('is_accurate', False)}")
            formatted.append(f"- Content snippet: {diagram_data.get('snippet', '')[:200]}")
        
        if "comparison_with_code" in data:
            comp_data = data["comparison_with_code"]
            formatted.append("\nCOMPARISON WITH CODE:")
            formatted.append(f"- Diagrams match code: {comp_data.get('matches_code', False)}")
            formatted.append(f"- Parallel claims verified: {comp_data.get('parallel_verified', False)}")
            formatted.append(f"- Misleading elements: {comp_data.get('misleading_elements', [])}")
        
        return "\n".join(formatted)