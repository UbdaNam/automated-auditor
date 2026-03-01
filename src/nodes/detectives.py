import json
from typing import Dict

from langgraph.graph import add_messages

from src.state import AgentState, Evidence
from src.tools.repo_tools import GitTools, ASTTools, FileSystemTools
from src.tools.doc_tools import PDFAnalyzer
from src.agents.detective_agents import (
    RepoInvestigatorAgent,
    DocAnalystAgent
    # VisionInspectorAgent  # Commented out - visual analysis unavailable
)


class DetectiveNodes:
    """Implementation of detective nodes for forensic evidence collection."""
    
    def __init__(self):
        # Initialize agents
        self.repo_investigator = RepoInvestigatorAgent()
        self.doc_analyst = DocAnalystAgent()
        # self.vision_inspector = VisionInspectorAgent()  # Commented out - visual analysis unavailable
        
        # Initialize tools
        self.git_tools = GitTools()
        self.ast_tools = ASTTools()
        self.file_tools = FileSystemTools()
        self.pdf_tools = PDFAnalyzer()
    
    def repo_investigator_node(self, state: AgentState) -> Dict:
        """RepoInvestigator node: analyzes code repository structure."""
        print("[RepoInvestigator] Starting forensic analysis...")
        
        try:
            # Extract repository
            repo_url = state["repo_url"]
            
            # Clone repository
            repo_path, repo_name = self.git_tools.clone_repository(repo_url)
            
            # Perform forensic analysis
            git_analysis = self.git_tools.analyze_git_history(repo_path)
            file_structure = self.file_tools.scan_directory_structure(repo_path)
            
            # Check key files
            state_file_check = self.file_tools.file_exists(f"{repo_path}/src/state.py")
            graph_file_check = self.file_tools.file_exists(f"{repo_path}/src/graph.py")
            
            # AST analysis on graph file if it exists
            ast_analysis = {}
            if graph_file_check["exists"]:
                ast_analysis = self.ast_tools.analyze_file_structure(
                    f"{repo_path}/src/graph.py"
                )
            
            # Combine forensic data
            forensic_data = {
                "git_analysis": git_analysis,
                "ast_analysis": ast_analysis,
                "file_structure": file_structure,
                "state_file_exists": state_file_check,
                "graph_file_exists": graph_file_check
            }
            
            # Get structured evidence from LLM agent
            evidence = self.repo_investigator.analyze_repository(forensic_data)
            
            # Add to state with parallel-safe operation
            evidence_key = "repo_evidence"
            
            return {
                "evidences": {
                    evidence_key: [evidence]
                }
            }
            
        except Exception as e:
            print(f"[RepoInvestigator] Error: {e}")
            
            # Return error evidence
            error_evidence = Evidence(
                goal="Analyze repository structure",
                found=False,
                content=f"Analysis failed: {e}",
                location="repository_root",
                rationale="Forensic analysis encountered an error",
                confidence=0.0
            )
            
            return {
                "evidences": {
                    "repo_error": [error_evidence]
                },
                "error": str(e),
                "error_context": "RepoInvestigator node failure"
            }
    
    def doc_analyst_node(self, state: AgentState) -> Dict:
        """DocAnalyst node: analyzes documentation and cross-references claims."""
        print("[DocAnalyst] Starting documentation analysis...")
        
        try:
            pdf_path = state["pdf_path"]
            
            # Extract text content from PDF
            content_result = self.pdf_tools.extract_text_from_pdf(pdf_path)
            
            # Search for key concepts
            key_concepts = [
                "Dialectical Synthesis",
                "Fan-In / Fan-Out", 
                "Metacognition",
                "State Synchronization",
                "LangGraph",
                "Parallel Execution"
            ]
            concept_analysis = self.pdf_tools.analyze_concept_depth(pdf_path, key_concepts)
            
            # Get cross-reference data from repo evidence if available
            code_evidence = {}
            if "repo_evidence" in state.get("evidences", {}):
                repo_evidences = state["evidences"]["repo_evidence"]
                if repo_evidences:
                    # Extract code structure info from evidence content
                    code_evidence = {
                        "python_files": [],
                        "has_parallel_wiring": "parallel" in str(repo_evidences[0].__dict__).lower(),
                        "has_state_graph": "stategraph" in str(repo_evidences[0].__dict__).lower()
                    }
            
            # Cross-reference claims
            cross_reference_result = self.pdf_tools.cross_reference_claims(
                pdf_path, code_evidence
            )
            
            # Combine forensic data
            forensic_data = {
                "content_analysis": content_result,
                "concept_analysis": concept_analysis["concept_analysis"] 
                               if concept_analysis["success"] else {},
                "cross_reference": cross_reference_result
            }
            
            # Get structured evidence from LLM agent
            evidence = self.doc_analyst.analyze_documentation(forensic_data)
            
            return {
                "evidences": {
                    "doc_evidence": [evidence]
                }
            }
            
        except Exception as e:
            print(f"[DocAnalyst] Error: {e}")
            
            error_evidence = Evidence(
                goal="Analyze documentation accuracy",
                found=False,
                content=f"Analysis failed: {e}",
                location="documentation",
                rationale="Document analysis encountered an error",
                confidence=0.0
            )
            
            return {
                "evidences": {
                    "doc_error": [error_evidence]
                },
                "error": str(e),
                "error_context": "DocAnalyst node failure"
            }
    
    # def vision_inspector_node(self, state: AgentState) -> Dict:
    #     """VisionInspector node: analyzes visual documentation."""
    #     print("[VisionInspector] Starting visual analysis...")
    #
    #     try:
    #         pdf_path = state["pdf_path"]
    #
    #         # Extract image references
    #         image_result = self.pdf_tools.extract_images_from_pdf(pdf_path)
    #
    #         # For this implementation, we'll focus on analyzing text references to diagrams
    #         # Full image analysis would require vision-capable models
    #
    #         # Create synthetic diagram analysis based on text content
    #         content_result = self.pdf_tools.extract_text_from_pdf(pdf_path)
    #
    #         # Simple pattern analysis for diagram types
    #         diagram_analysis = self._analyze_diagram_patterns(
    #             content_result["content"] if content_result["success"] else ""
    #         )
    #
    #         # Combine forensic data
    #         forensic_data = {
    #             "image_analysis": image_result,
    #             "diagram_content": diagram_analysis,
    #             "comparison_with_code": self._compare_with_code(state)
    #         }
    #
    #         # Get structured evidence from LLM agent
    #         evidence = self.vision_inspector.analyze_visuals(forensic_data)
    #
    #         return {
    #             "evidences": {
    #                 "vision_evidence": [evidence]
    #             }
    #         }
    #
    #     except Exception as e:
    #         print(f"[VisionInspector] Error: {e}")
    #
    #         error_evidence = Evidence(
    #             goal="Analyze visual documentation",
    #             found=False,
    #             content=f="Analysis failed: {e}",
    #             location="visual_content",
    #             rationale="Visual analysis encountered an error",
    #             confidence=0.0
    #         )
    #
    #         return {
    #             "evidences": {
    #                 "vision_error": [error_evidence]
    #             },
    #             "error": str(e),
    #             "error_context": "VisionInspector node failure"
    #         }
    
    # def _analyze_diagram_patterns(self, text_content: str) -> Dict:
    #     """Analyze text for diagram patterns."""
    #     text_lower = text_content.lower()
    #
    #     diagram_type = "generic"
    #     has_parallel_flow = False
    #     is_accurate = False
    #
    #     # Detect diagram type
    #     if "stategraph" in text_lower or "langgraph" in text_lower:
    #         diagram_type = "StateGraph"
    #     elif "sequence" in text_lower and "diagram" in text_lower:
    #         diagram_type = "sequence"
    #     elif "flowchart" in text_lower:
    #         diagram_type = "flowchart"
    #
    #     # Check for parallel flow patterns
    #     parallel_patterns = [
    #         "parallel", "concurrent", "fan-out", "fan-in",
    #         "detectives.*judges", "multiple agents", "simultaneous"
    #     ]
    #
    #     for pattern in parallel_patterns:
    #         if pattern in text_lower:
    #             has_parallel_flow = True
    #             break
    #
    #     # Check for accurate architecture description
    #     accurate_patterns = [
    #         "detectives.*evidence.*judges.*synthesis",
    #         "parallel.*aggregation",
    #         "fan-out.*fan-in"
    #     ]
    #
    #     for pattern in accurate_patterns:
    #         if any(keyword in text_lower for keyword in pattern.split(".*")):
    #             is_accurate = True
    #             break
    #
    #     return {
    #         "type": diagram_type,
    #         "has_parallel_flow": has_parallel_flow,
    #         "is_accurate": is_accurate,
    #         "snippet": text_content[:500] if text_content else ""
    #     }
    
    # def _compare_with_code(self, state: AgentState) -> Dict:
    #     """Compare visual claims with code evidence."""
    #     matches_code = False
    #     parallel_verified = False
    #     misleading_elements = []
    #
    #     # Basic comparison logic - could be enhanced with actual code evidence
    #     if "repo_evidence" in state.get("evidences", {}):
    #         repo_content = str(state["evidences"]["repo_evidence"])
    #
    #         matches_code = "stategraph" in repo_content.lower()
    #         parallel_verified = "parallel" in repo_content.lower()
    #
    #     return {
    #         "matches_code": matches_code,
    #         "parallel_verified": parallel_verified,
    #         "misleading_elements": misleading_elements
    #     }


def evidence_aggregator_node(state: AgentState) -> Dict:
    """Aggregate evidence from all detectives and prepare for judicial layer."""
    print("[EvidenceAggregator] Aggregating forensic evidence...")
    print(f"[Debug] State keys: {list(state.keys())}")
    print(f"[Debug] Available evidence keys: {list(state.get('evidences', {}).keys())}")
    
    # Collect all evidence
    all_evidence = {}
    total_evidence = 0
    errors = []
    
    for evidence_key, evidence_list in state.get("evidences", {}).items():
        all_evidence[evidence_key] = evidence_list
        total_evidence += len(evidence_list)
        
        # Collect errors
        if "error" in evidence_key:
            errors.extend(evidence_list)
    
    # Prepare aggregated state for judges
    aggregation_result = {
        "evidence_summary": {
            "total_sources": len(all_evidence),
            "total_evidence_items": total_evidence,
            "error_count": len(errors),
            "evidence_keys": list(all_evidence.keys())
        }
    }
    
    print(f"[EvidenceAggregator] Aggregated {total_evidence} evidence items from {len(all_evidence)} sources")
    print(f"[Debug] Errors: {errors}")
    print(f"[Debug] Summary: {aggregation_result}")
    
    return {"aggregated_evidence": aggregation_result}