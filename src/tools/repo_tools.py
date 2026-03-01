import ast
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class GitTools:
    """Tools for forensic analysis of git repositories using system git commands."""
    
    @staticmethod
    def clone_repository(repo_url: str) -> Tuple[str, str]:
        """
        Safely clone a repository using system git command.
        
        Args:
            repo_url: URL of the repository to clone
            
        Returns:
            Tuple of (repo_path, repo_name)
        """
        try:
            # Create permanent directory for cloning
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            permanent_dir = "./temp_repos"
            os.makedirs(permanent_dir, exist_ok=True)
            repo_path = Path(permanent_dir) / repo_name
            
            # Clone using system git command
            result = subprocess.run(
                ["git", "clone", repo_url, str(repo_path)],
                capture_output=True,
                text=True,
                check=True
            )
            
            return str(repo_path), repo_name
            
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Git clone failed: {e.stderr}")
        except Exception as e:
            raise ValueError(f"Repository cloning failed: {e}")
    
    @staticmethod
    def analyze_git_history(repo_path: str) -> Dict:
        """
        Analyze git commit history using git log command.
        
        Args:
            repo_path: Path to the git repository
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Get git log output
            result = subprocess.run(
                ["git", "log", "--oneline", "-50", "--format=%H|%an|%ad|%s"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 3)
                    if len(parts) == 4:
                        commits.append({
                            "hash": parts[0][:8],
                            "author": parts[1],
                            "date": parts[2],
                            "message": parts[3].strip()
                        })
            
            return {
                "total_commits": len(commits),
                "recent_commits": commits,
                "has_progression": GitTools._check_progression_pattern(commits),
                "has_atomic_history": GitTools._check_atomic_history(commits)
            }
            
        except subprocess.CalledProcessError as e:
            return {"error": f"Git log failed: {e.stderr}"}
        except Exception as e:
            return {"error": f"Failed to analyze git history: {e}"}
    
    @staticmethod
    def _check_progression_pattern(commits: List[Dict]) -> bool:
        """Check if commits show progressive development patterns."""
        if len(commits) < 5:
            return False
        
        # Check for feature-related keywords
        feature_words = ["feature", "add", "implement", "fix", "update", "refactor"]
        feature_count = sum(1 for commit in commits if any(word in commit["message"].lower() for word in feature_words))
        
        return feature_count >= len(commits) * 0.3  # At least 30% of commits show progression
    
    @staticmethod
    def _check_atomic_history(commits: List[Dict]) -> bool:
        """Check if commits follow atomic commit principles."""
        if len(commits) < 5:
            return False
        
        # Check for focused commit messages (not too long, not multiple unrelated changes)
        focused_count = sum(1 for commit in commits 
                          if len(commit["message"]) < 100 and 
                          commit["message"].count("and") < 3)
        
        return focused_count >= len(commits) * 0.6  # At least 60% of commits are atomic


class ASTTools:
    """Tools for analyzing Python code structure using AST."""
    
    @staticmethod
    def analyze_file_structure(file_path: str) -> Dict:
        """
        Analyze Python file structure using AST.
        
        Args:
            file_path: Path to Python file to analyze
            
        Returns:
            Dictionary with structure analysis
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Count different types of nodes
            imports = []
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend([name.name for name in node.names])
                elif isinstance(node, ast.ImportFrom):
                    imports.extend([name.name for name in node.names])
                elif isinstance(node, ast.FunctionDef):
                    functions.append({"name": node.name, "line": node.lineno})
                elif isinstance(node, ast.ClassDef):
                    classes.append({"name": node.name, "line": node.lineno})
            
            return {
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "has_state_graph": ASTTools._check_state_graph_structure(tree),
                "has_parallel_wiring": ASTTools._check_parallel_wiring(tree)
            }
            
        except Exception as e:
            return {"error": f"AST analysis failed: {e}"}
    
    @staticmethod
    def _check_state_graph_structure(tree: ast.AST) -> bool:
        """Check if code has LangGraph StateGraph structure."""
        # Look for LangGraph patterns
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if "StateGraph" in [b.id for b in node.bases if isinstance(b, ast.Name)]:
                    return True
        return False
    
    @staticmethod
    def _check_parallel_wiring(tree: ast.AST) -> bool:
        """Check for parallel execution patterns."""
        # Look for branching/parallel patterns
        for node in ast.walk(tree):
            if isinstance(node, ast.If) or isinstance(node, ast.Match):
                return True
        return False


class FileSystemTools:
    """Tools for general file system forensics."""
    
    @staticmethod
    def scan_directory_structure(repo_path: str) -> Dict:
        """
        Scan directory structure and file statistics.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            Dictionary with directory analysis
        """
        try:
            data = {}
            
            # Count files by type
            file_counts = {}
            total_files = 0
            
            for root, dirs, files in os.walk(repo_path):
                for file in files:
                    ext = os.path.splitext(file)[1] or "no_extension"
                    file_counts[ext] = file_counts.get(ext, 0) + 1
                    total_files += 1
            
            return {
                "total_files": total_files,
                "file_types": file_counts,
                "has_readme": FileSystemTools.file_exists(os.path.join(repo_path, "README.md")),
                "has_pyproject": FileSystemTools.file_exists(os.path.join(repo_path, "pyproject.toml")),
                "has_requirements": FileSystemTools.file_exists(os.path.join(repo_path, "requirements.txt"))
            }
            
        except Exception as e:
            return {"error": f"Directory scan failed: {e}"}
    
    @staticmethod
    def file_exists(file_path: str) -> Dict:
        """Check if file exists and return basic info."""
        try:
            if os.path.exists(file_path):
                return {"exists": True, "size": os.path.getsize(file_path)}
            else:
                return {"exists": False}
        except Exception:
            return {"exists": False}