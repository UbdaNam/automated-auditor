import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from docling.document_converter import DocumentConverter


class PDFAnalyzer:
    """Tools for analyzing PDF documents and extracting forensic evidence."""
    
    def __init__(self):
        self.converter = DocumentConverter()
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict:
        """
        Extract text content from PDF document.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted content
        """
        try:
            result = self.converter.convert(pdf_path)
            
            if hasattr(result, 'document') and result.document:
                text_content = str(result.document)
            else:
                text_content = str(result)
            
            return {
                "success": True,
                "content": text_content,
                "length": len(text_content),
                "pages": self._estimate_pages(text_content) if text_content else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"PDF extraction failed: {e}",
                "content": "",
                "length": 0,
                "pages": 0
            }
    
    def extract_images_from_pdf(self, pdf_path: str) -> Dict:
        """
        Extract images from PDF for visual analysis.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with image extraction info
        """
        try:
            # Note: Full image extraction can be implemented with other libraries
            # For now, we'll detect image references in the text
            
            result = self.converter.convert(pdf_path)
            
            if hasattr(result, 'document') and result.document:
                text_content = str(result.document)
            else:
                text_content = str(result)
            
            # Look for image references
            image_patterns = [
                r"Figure \d+",
                r"Image \d+",
                r"Diagram",
                r"Chart",
                r"Graph",
                r"Screenshot"
            ]
            
            image_references = []
            for pattern in image_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                image_references.extend(matches)
            
            return {
                "success": True,
                "image_references": list(set(image_references)),
                "total_references": len(set(image_references)),
                "content_snippet": text_content[:500] + "..." if len(text_content) > 500 else text_content
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Image extraction failed: {e}",
                "image_references": [],
                "total_references": 0,
                "content_snippet": ""
            }
    
    def search_keywords_in_pdf(self, pdf_path: str, keywords: List[str]) -> Dict:
        """
        Search for specific keywords in PDF content.
        
        Args:
            pdf_path: Path to PDF file
            keywords: List of keywords to search for
            
        Returns:
            Dictionary with keyword matches
        """
        try:
            result = self.extract_text_from_pdf(pdf_path)
            if not result["success"]:
                return result
            
            text_content = result["content"].lower()
            keyword_matches = {}
            
            for keyword in keywords:
                matches = re.findall(keyword.lower(), text_content, re.IGNORECASE)
                keyword_matches[keyword] = {
                    "count": len(matches),
                    "contexts": self._get_keyword_context(text_content, keyword.lower(), matches)
                }
            
            return {
                "success": True,
                "keyword_matches": keyword_matches,
                "total_keywords_found": sum(len(matches) for matches in keyword_matches.values())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Keyword search failed: {e}",
                "keyword_matches": {},
                "total_keywords_found": 0
            }
    
    def analyze_concept_depth(self, pdf_path: str, concepts: List[str]) -> Dict:
        """
        Analyze depth of understanding for specific concepts.
        
        Args:
            pdf_path: Path to PDF file
            concepts: List of concepts to analyze
            
        Returns:
            Dictionary with concept analysis
        """
        try:
            result = self.extract_text_from_pdf(pdf_path)
            if not result["success"]:
                return result
            
            text_content = result["content"]
            concept_analysis = {}
            
            for concept in concepts:
                # Look for deep explanations vs. buzzword usage
                concept_lower = concept.lower()
                
                # Count occurrences
                occurrences = text_content.lower().count(concept_lower)
                
                # Look for explanatory context around the concept
                explanations = self._find_explanatory_context(text_content, concept_lower)
                
                concept_analysis[concept] = {
                    "occurrences": occurrences,
                    "has_deep_explanation": len(explanations) > 0,
                    "explanatory_contexts": explanations,
                    "is_buzzword": occurrences > 0 and len(explanations) == 0,
                    "depth_score": self._calculate_concept_depth_score(occurrences, explanations)
                }
            
            return {
                "success": True,
                "concept_analysis": concept_analysis
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Concept analysis failed: {e}",
                "concept_analysis": {}
            }
    
    def cross_reference_claims(self, pdf_path: str, code_evidence: Dict) -> Dict:
        """
        Cross-reference claims made in PDF with actual code evidence.
        
        Args:
            pdf_path: Path to PDF file
            code_evidence: Evidence from code analysis
            
        Returns:
            Dictionary with cross-reference results
        """
        try:
            result = self.extract_text_from_pdf(pdf_path)
            if not result["success"]:
                return result
            
            text_content = result["content"]
            
            # Extract file paths mentioned in PDF
            file_path_pattern = r"(?:src/|\b\w+\.py\b|\w+/\w+\.py)"
            file_mentions = re.findall(file_path_pattern, text_content)
            
            # Normalize mentions and code evidence
            mentioned_files = list(set(file_mentions))
            existing_files = code_evidence.get("python_files", [])
            
            # Compare mentions vs reality
            verified_files = []
            hallucinated_files = []
            
            for mentioned_file in mentioned_files:
                # Simple check if file exists in code evidence
                exists = any(mentioned_file in existing_file 
                           for existing_file in existing_files)
                
                if exists:
                    verified_files.append(mentioned_file)
                else:
                    hallucinated_files.append(mentioned_file)
            
            # Feature claims analysis
            feature_claims = self._extract_feature_claims(text_content)
            feature_verification = self._verify_feature_claims(feature_claims, code_evidence)
            
            return {
                "success": True,
                "mentioned_files": mentioned_files,
                "verified_files": verified_files,
                "hallucinated_files": hallucinated_files,
                "hallucination_rate": len(hallucinated_files) / max(len(mentioned_files), 1),
                "feature_claims": feature_claims,
                "feature_verification": feature_verification
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Cross-reference failed: {e}",
                "mentioned_files": [],
                "verified_files": [],
                "hallucinated_files": [],
                "hallucination_rate": 1.0,
                "feature_claims": [],
                "feature_verification": []
            }
    
    def _estimate_pages(self, text: str) -> int:
        """Estimate number of pages based on text length."""
        # Rough estimate: 500 words per page
        word_count = len(text.split())
        return max(1, word_count // 500)
    
    def _get_keyword_context(self, text: str, keyword: str, matches: List[str]) -> List[str]:
        """Extract context around keyword matches."""
        contexts = []
        
        for match in matches:
            start = text.lower().find(keyword)
            if start != -1:
                # Get surrounding 100 characters
                context_start = max(0, start - 50)
                context_end = min(len(text), start + len(keyword) + 50)
                contexts.append(text[context_start:context_end].strip())
                
        return contexts[:5]  # Return top 5 contexts
    
    def _find_explanatory_context(self, text: str, concept: str) -> List[str]:
        """Find explanatory context around concept mentions."""
        # Look for sentences that explain the concept
        sentences = re.split(r'[.!?]+', text)
        explanations = []
        
        for sentence in sentences:
            if concept.lower() in sentence.lower():
                # Check if this sentence contains explanatory language
                explanatory_words = ["means", "implements", "achieves", "enables",
                                   "facilitates", "executes", "process"]
                
                if any(word in sentence.lower() for word in explanatory_words):
                    explanations.append(sentence.strip())
        
        return explanations
    
    def _calculate_concept_depth_score(self, occurrences: int, explanations: List[str]) -> float:
        """Calculate a depth score for concept understanding."""
        if occurrences == 0:
            return 0.0
        
        # Score based on ratio of explanations to mentions
        explanation_ratio = len(explanations) / occurrences
        
        if explanation_ratio > 0.5:
            return 0.8  # Deep understanding
        elif explanation_ratio > 0.2:
            return 0.5  # Some understanding
        else:
            return 0.2  # Buzzword usage
    
    def _extract_feature_claims(self, text: str) -> List[Dict]:
        """Extract feature claims from text."""
        # Patterns for feature claims
        patterns = [
            r"(?:implemented|built|created|added|designed)\s+(?:a|the|an)?\s*([^.,!?]+?)\s+(?:feature|function|component|system)",
            r"We\s+(?:implement|create|build)\s+([^.,!?]+)",
            r"The\s+([^.,!?]+?)\s+(?:is|are)\s+(?:implemented|created|built)"
        ]
        
        claims = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                claims.append({
                    "claim": match.strip(),
                    "pattern": pattern
                })
        
        return claims
    
    def _verify_feature_claims(self, claims: List[Dict], code_evidence: Dict) -> List[Dict]:
        """Verify feature claims against code evidence."""
        verified_claims = []
        
        for claim in claims:
            claim_text = claim["claim"].lower()
            
            # Simple check against code components
            has_graph_wiring = code_evidence.get("has_parallel_wiring", False)
            has_state_graph = code_evidence.get("has_state_graph", False)
            
            # Check if claim matches code evidence
            verification = {
                "claim": claim["claim"],
                "mentions_graph": "graph" in claim_text,
                "mentions_parallel": any(word in claim_text 
                                      for word in ["parallel", "concurrent", "fan-out"]),
                "mentions_detectives": any(word in claim_text 
                                      for word in ["detective", "investigator", "analyst"]),
                "matches_code_graph": has_graph_wiring and "graph" in claim_text,
                "matches_code_parallel": has_graph_wiring and any(word in claim_text
                                                                 for word in ["parallel", "concurrent", "fan-out"])
            }
            
            verified_claims.append(verification)
        
        return verified_claims