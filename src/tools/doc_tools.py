from typing import List, Dict
import PyPDF2
import re

def ingest_pdf(pdf_path: str) -> str:
    """Extract text content from PDF."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except FileNotFoundError:
        raise Exception(f"PDF file not found: {pdf_path}")
    except Exception as e:
        raise Exception(f"Failed to parse PDF: {str(e)}")

def query_document_content(document_text: str, query_terms: List[str]) -> Dict[str, List[str]]:
    """Query document for specific terms and return context."""
    results = {}
    
    # Split text into paragraphs instead of lines for better context
    paragraphs = re.split(r'\n\s*\n', document_text)
    
    for term in query_terms:
        contexts = []
        for paragraph in paragraphs:
            if term.lower() in paragraph.lower():
                # Clean up the paragraph text
                cleaned_paragraph = re.sub(r'\s+', ' ', paragraph).strip()
                if cleaned_paragraph:  # Only add non-empty paragraphs
                    contexts.append(cleaned_paragraph)
        results[term] = contexts
    
    return results

def extract_key_concepts(document_text: str) -> Dict[str, List[str]]:
    """Extract key concepts and technical terms from document."""
    # Common technical terms we're interested in
    technical_terms = [
        "Dialectical Synthesis", 
        "Fan-In / Fan-Out", 
        "Metacognition", 
        "State Synchronization",
        "StateGraph",
        "LangGraph",
        "Pydantic",
        "AST",
        "Parallel Execution",
        "Judicial Layer",
        "Detective Layer",
        "Chief Justice"
    ]
    
    return query_document_content(document_text, technical_terms)

def find_file_references(document_text: str) -> List[str]:
    """Find file path references in document."""
    # Regular expression to match file paths
    file_pattern = r'(?:src/|\.\/)[\w\/\-\.]+\.[\w]+'
    file_matches = re.findall(file_pattern, document_text)
    return list(set(file_matches))  # Remove duplicates