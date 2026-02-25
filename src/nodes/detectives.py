from typing import Dict, List
import os
from ..tools.repo_tools import clone_repository, extract_git_history, analyze_graph_structure, find_files_with_extension
from ..tools.doc_tools import ingest_pdf, query_document_content, extract_key_concepts, find_file_references
from ..state import Evidence

class RepoInvestigator:
    """Investigates repository structure and code artifacts."""
    
    def __init__(self):
        pass
    
    def investigate_codebase(self, repo_url: str) -> Dict[str, List[Evidence]]:
        """Investigate repository structure and code artifacts."""
        try:
            # Clone repository safely
            temp_dir = clone_repository(repo_url)
            
            # Collect evidence
            evidences = []
            
            # Evidence: Git History Analysis
            git_commits = extract_git_history(temp_dir)
            evidences.append(Evidence(
                goal="Git Forensic Analysis",
                found=len(git_commits) > 3,
                content=str(git_commits[:10]),  # First 10 commits
                location=temp_dir,
                rationale=f"Found {len(git_commits)} commits showing development progression",
                confidence=0.9 if len(git_commits) > 3 else 0.3
            ))
            
            # Evidence: State Management Check
            state_files = []
            for root, dirs, files in os.walk(temp_dir):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if file in ["state.py", "graph.py"]:
                        state_files.append(os.path.join(root, file))
            
            state_management_evidence = []
            for file_path in state_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "BaseModel" in content or "TypedDict" in content:
                            state_management_evidence.append(f"Found in {file_path}")
                except:
                    pass
            
            evidences.append(Evidence(
                goal="State Management Rigor",
                found=len(state_management_evidence) > 0,
                content=str(state_management_evidence),
                location=str(state_files),
                rationale=f"Found {len(state_management_evidence)} files with Pydantic BaseModel or TypedDict definitions",
                confidence=0.8 if len(state_management_evidence) > 0 else 0.2
            ))
            
            # Evidence: Graph Orchestration Check
            graph_files = find_files_with_extension(temp_dir, ".py")
            graph_analysis_evidence = []
            
            for file_path in graph_files:
                try:
                    structure_analysis = analyze_graph_structure(file_path)
                    if structure_analysis["stategraph_found"] or structure_analysis["edges"]:
                        graph_analysis_evidence.append({
                            "file": file_path,
                            "analysis": structure_analysis
                        })
                except:
                    pass
                    
            evidences.append(Evidence(
                goal="Graph Orchestration",
                found=len(graph_analysis_evidence) > 0,
                content=str(graph_analysis_evidence),
                location=str([item["file"] for item in graph_analysis_evidence]),
                rationale=f"Found {len(graph_analysis_evidence)} Python files with graph structure elements",
                confidence=0.7 if len(graph_analysis_evidence) > 0 else 0.3
            ))
            
            # Evidence: Safe Tool Engineering Check
            python_files = find_files_with_extension(temp_dir, ".py")
            unsafe_patterns = []
            
            for file_path in python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Check for unsafe patterns
                        if "os.system" in content and "subprocess" not in content:
                            unsafe_patterns.append(file_path)
                        elif "eval(" in content:
                            unsafe_patterns.append(file_path)
                except:
                    pass
            
            evidences.append(Evidence(
                goal="Safe Tool Engineering",
                found=len(unsafe_patterns) == 0,
                content=str(unsafe_patterns) if unsafe_patterns else "No unsafe patterns found",
                location=repo_url,
                rationale=f"Checked {len(python_files)} Python files for unsafe patterns",
                confidence=0.9 if len(unsafe_patterns) == 0 else 0.2
            ))
            
            return {"repository": evidences}
        except Exception as e:
            return {"repository": [Evidence(
                goal="Repository Investigation",
                found=False,
                content=str(e),
                location=repo_url,
                rationale="Failed to investigate repository",
                confidence=0.1
            )]}

class DocAnalyst:
    """Analyzes accompanying documentation for theoretical depth."""
    
    def __init__(self):
        pass
    
    def analyze_document(self, pdf_path: str) -> Dict[str, List[Evidence]]:
        """Analyze PDF report for theoretical depth and accuracy."""
        try:
            # Ingest PDF content
            document_text = ingest_pdf(pdf_path)
            
            # Query for key concepts
            key_terms = [
                "Dialectical Synthesis", 
                "Fan-In / Fan-Out", 
                "Metacognition", 
                "State Synchronization",
                "LangGraph",
                "StateGraph"
            ]
            
            query_results = query_document_content(document_text, key_terms)
            
            evidences = []
            for term, contexts in query_results.items():
                evidences.append(Evidence(
                    goal=f"Theoretical Depth - {term}",
                    found=len(contexts) > 0,
                    content=str(contexts[:3]),  # First 3 contexts
                    location=pdf_path,
                    rationale=f"Found {len(contexts)} mentions of '{term}' with contextual explanations",
                    confidence=0.8 if len(contexts) > 0 else 0.2
                ))
            
            # Evidence: Host Analysis Accuracy (file references)
            file_references = find_file_references(document_text)
            evidences.append(Evidence(
                goal="Host Analysis Accuracy",
                found=len(file_references) > 0,
                content=str(file_references),
                location=pdf_path,
                rationale=f"Found {len(file_references)} file path references in document",
                confidence=0.7
            ))
            
            return {"document": evidences}
        except Exception as e:
            return {"document": [Evidence(
                goal="Document Analysis",
                found=False,
                content=str(e),
                location=pdf_path,
                rationale="Failed to analyze document",
                confidence=0.1
            )]}

# Example usage:
# repo_investigator = RepoInvestigator()
# evidences = repo_investigator.investigate_codebase("https://github.com/example/repo.git")
#
# doc_analyst = DocAnalyst()
# doc_evidences = doc_analyst.analyze_document("path/to/report.pdf")