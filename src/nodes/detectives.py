from typing import Dict, List, Optional
import os
from ..tools.repo_tools import clone_repository, extract_git_history, analyze_graph_structure, find_files_with_extension
from ..tools.doc_tools import ingest_pdf, query_document_content, extract_key_concepts, find_file_references
from ..state import Evidence

class RepoInvestigator:
    """Investigates repository structure and code artifacts."""
    
    def __init__(self):
        pass
    
    def investigate_codebase(self, repo_url: str, rubric_dimensions: Optional[List[Dict]] = None) -> Dict[str, List[Evidence]]:
        """Investigate repository structure and code artifacts, guided by rubric dimensions when provided."""
        try:
            # Clone repository safely
            temp_dir = clone_repository(repo_url)
            
            # Collect evidence using rubric guidance when available
            evidences = []
            
            # If rubric dimensions are provided, use them for targeted investigation
            if rubric_dimensions:
                # Filter dimensions relevant to repository investigation
                repo_dimensions = [
                    dim for dim in rubric_dimensions
                    if dim.get("target_artifact") == "github_repo"
                ]
                
                # Apply rubric-guided investigations
                for dimension in repo_dimensions:
                    forensic_instruction = dimension.get("forensic_instruction", "")
                    dimension_id = dimension.get("id", "unknown")
                    
                    # Perform rubric-specific investigations
                    if "git log" in forensic_instruction.lower():
                        # Evidence: Git History Analysis (rubric-guided)
                        git_commits = extract_git_history(temp_dir)
                        evidences.append(Evidence(
                            goal=f"Git Forensic Analysis - {dimension_id}",
                            found=len(git_commits) > 3,
                            content=str(git_commits[:10]),  # First 10 commits
                            location=temp_dir,
                            rationale=f"Found {len(git_commits)} commits showing development progression per rubric requirement",
                            confidence=0.9 if len(git_commits) > 3 else 0.3
                        ))
                    
                    elif "stategraph" in forensic_instruction.lower() or "typeddict" in forensic_instruction.lower():
                        # Evidence: State Management Rigor (rubric-guided)
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
                            goal=f"State Management Rigor - {dimension_id}",
                            found=len(state_management_evidence) > 0,
                            content=str(state_management_evidence),
                            location=str(state_files),
                            rationale=f"Found {len(state_management_evidence)} files with Pydantic BaseModel or TypedDict definitions per rubric requirement",
                            confidence=0.8 if len(state_management_evidence) > 0 else 0.2
                        ))
                    
                    elif "add_edge" in forensic_instruction.lower() or "parallel" in forensic_instruction.lower():
                        # Evidence: Graph Orchestration (rubric-guided)
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
                            goal=f"Graph Orchestration - {dimension_id}",
                            found=len(graph_analysis_evidence) > 0,
                            content=str(graph_analysis_evidence),
                            location=str([item["file"] for item in graph_analysis_evidence]),
                            rationale=f"Found {len(graph_analysis_evidence)} Python files with graph structure elements per rubric requirement",
                            confidence=0.7 if len(graph_analysis_evidence) > 0 else 0.3
                        ))
            
            # If no rubric guidance or fallback to default investigations
            if not evidences:
                # Evidence: Git History Analysis (default)
                git_commits = extract_git_history(temp_dir)
                evidences.append(Evidence(
                    goal="Git Forensic Analysis",
                    found=len(git_commits) > 3,
                    content=str(git_commits[:10]),  # First 10 commits
                    location=temp_dir,
                    rationale=f"Found {len(git_commits)} commits showing development progression",
                    confidence=0.9 if len(git_commits) > 3 else 0.3
                ))
                
                # Evidence: State Management Check (default)
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
                
                # Evidence: Graph Orchestration Check (default)
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
    
    def analyze_document(self, pdf_path: str, rubric_dimensions: Optional[List[Dict]] = None) -> Dict[str, List[Evidence]]:
        """Analyze PDF report for theoretical depth and accuracy, guided by rubric dimensions when provided."""
        try:
            # Ingest PDF content
            document_text = ingest_pdf(pdf_path)
            
            evidences = []
            
            # If rubric dimensions are provided, use them for targeted investigation
            if rubric_dimensions:
                # Filter dimensions relevant to document investigation
                doc_dimensions = [
                    dim for dim in rubric_dimensions
                    if dim.get("target_artifact") == "pdf_report"
                ]
                
                # Apply rubric-guided investigations
                for dimension in doc_dimensions:
                    forensic_instruction = dimension.get("forensic_instruction", "")
                    dimension_id = dimension.get("id", "unknown")
                    
                    # Perform rubric-specific investigations
                    if "dialectical synthesis" in forensic_instruction.lower() or "fan-in" in forensic_instruction.lower():
                        # Evidence: Theoretical Depth (rubric-guided)
                        key_terms = [
                            "Dialectical Synthesis",
                            "Fan-In / Fan-Out",
                            "Metacognition",
                            "State Synchronization",
                            "LangGraph",
                            "StateGraph"
                        ]
                        
                        query_results = query_document_content(document_text, key_terms)
                        
                        for term, contexts in query_results.items():
                            evidences.append(Evidence(
                                goal=f"Theoretical Depth - {term} - {dimension_id}",
                                found=len(contexts) > 0,
                                content=str(contexts[:3]),  # First 3 contexts
                                location=pdf_path,
                                rationale=f"Found {len(contexts)} mentions of '{term}' with contextual explanations per rubric requirement",
                                confidence=0.8 if len(contexts) > 0 else 0.2
                            ))
                    
                    elif "file path" in forensic_instruction.lower() or "citation" in forensic_instruction.lower():
                        # Evidence: Host Analysis Accuracy (rubric-guided)
                        file_references = find_file_references(document_text)
                        evidences.append(Evidence(
                            goal=f"Host Analysis Accuracy - {dimension_id}",
                            found=len(file_references) > 0,
                            content=str(file_references),
                            location=pdf_path,
                            rationale=f"Found {len(file_references)} file path references in document per rubric requirement",
                            confidence=0.7
                        ))
            
            # If no rubric guidance or fallback to default investigations
            if not evidences:
                # Evidence: Theoretical Depth (default)
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
                
                # Evidence: Host Analysis Accuracy (default)
                file_references = find_file_references(document_text)
                evidences.append(Evidence(
                    goal="Host Analysis Accuracy",
                    found=len(file_references) > 0,
                    content=str(file_references),
                    location=pdf_path,
                    rationale=f"Found {len(file_references)} file path references in document",
                    confidence=0.7
                ))
            
            # Evidence: Safe Tool Engineering Check
            unsafe_patterns = []
            # Check document for unsafe patterns or security concerns
            unsafe_terms = ["unsafe", "insecure", "vulnerability", "exploit"]
            for term in unsafe_terms:
                if term in document_text.lower():
                    unsafe_patterns.append(term)
            
            evidences.append(Evidence(
                goal="Safe Documentation Practices",
                found=len(unsafe_patterns) == 0,
                content=str(unsafe_patterns) if unsafe_patterns else "No unsafe terms found",
                location=pdf_path,
                rationale=f"Checked document for {len(unsafe_terms)} unsafe terms",
                confidence=0.9 if len(unsafe_patterns) == 0 else 0.2
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