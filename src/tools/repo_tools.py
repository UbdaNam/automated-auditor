import tempfile
import subprocess
import os
from pathlib import Path
from typing import List, Dict
import ast

def clone_repository(repo_url: str) -> str:
    """Clone repository to a temporary directory."""
    temp_dir = tempfile.mkdtemp()
    try:
        # Using shell=False for security
        result = subprocess.run(
            ["git", "clone", repo_url, temp_dir], 
            check=True, 
            capture_output=True, 
            text=True
        )
        return temp_dir
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to clone repository: {e.stderr}")

def extract_git_history(repo_path: str) -> List[Dict]:
    """Extract git commit history with timestamps."""
    try:
        # Get commit history with dates
        result = subprocess.run([
            "git", "-C", repo_path, "log", "--oneline", "--reverse", "--date=iso", "--pretty=format:%H|%ad|%s"
        ], capture_output=True, text=True, check=True)
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|', 2)
                if len(parts) >= 3:
                    commits.append({
                        "hash": parts[0],
                        "timestamp": parts[1],
                        "message": parts[2]
                    })
        return commits
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to extract git history: {e.stderr}")

def analyze_graph_structure(file_path: str) -> Dict:
    """Analyze LangGraph structure using AST parsing."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Look for StateGraph instantiation and add_edge calls
        findings = {
            "stategraph_found": False,
            "parallel_execution": False,
            "edges": [],
            "nodes": []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for StateGraph instantiation
                if isinstance(node.func, ast.Name) and "StateGraph" in node.func.id:
                    findings["stategraph_found"] = True
                
                # Check for add_edge calls indicating graph wiring
                if isinstance(node.func, ast.Attribute) and node.func.attr == "add_edge":
                    edge_info = {
                        "line": node.lineno,
                        "args": [ast.dump(arg) for arg in node.args]
                    }
                    findings["edges"].append(edge_info)
                    
                    # Check for parallel wiring pattern
                    if len(node.args) >= 2:
                        findings["parallel_execution"] = True
                        
            # Look for node definitions
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and "node" in target.id.lower():
                        findings["nodes"].append({
                            "line": node.lineno,
                            "name": target.id
                        })
        
        return findings
    except FileNotFoundError:
        raise Exception(f"File not found: {file_path}")
    except SyntaxError as e:
        raise Exception(f"Syntax error in file {file_path}: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to analyze graph structure: {str(e)}")

def find_files_with_extension(repo_path: str, extension: str) -> List[str]:
    """Find all files with a specific extension in the repository."""
    files = []
    for root, dirs, filenames in os.walk(repo_path):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for filename in filenames:
            if filename.endswith(extension):
                files.append(os.path.join(root, filename))
    return files