"""
Judge Agents for Layer 2 Judicial Processing.
Three personas: Prosecutor, Defense, TechLead
Each evaluates evidence independently with structured output.
"""

from typing import Dict, List, Any, Optional
import asyncio
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from src.state import JudicialOpinion


class JudgeAgent:
    """Base class for judge agents with common functionality."""
    
    def __init__(self, persona: str, model_name: str = "gpt-4o-mini"):
        self.persona = persona
        self.llm = ChatOpenAI(model=model_name, temperature=0.7)
        self.structured_llm = self.llm.with_structured_output(JudicialOpinion)
    
    def _build_prompt(self, criterion: Dict[str, Any], evidence: str) -> str:
        """Build evaluation prompt for the specific persona."""
        raise NotImplementedError("Subclasses must implement build_prompt")
    
    async def evaluate(self, criterion: Dict[str, Any], evidence: str) -> JudicialOpinion:
        """Evaluate evidence against the criterion."""
        prompt = self._build_prompt(criterion, evidence)
        
        try:
            # Use structured output to enforce JudicialOpinion schema
            opinion_dict = await self.structured_llm.ainvoke(prompt)
            
            # Convert persona string to the required format
            if self.persona == "Prosecutor":
                judge_type = "Prosecutor"
            elif self.persona == "Defense":
                judge_type = "Defense"
            else:
                judge_type = "TechLead"
            
            opinion = JudicialOpinion(
                judge=judge_type,
                criterion_id=criterion["id"],
                score=opinion_dict.get("score", 3),
                argument=opinion_dict.get("argument", "Evaluation completed"),
                cited_evidence=opinion_dict.get("cited_evidence", [])
            )
            return opinion
        except Exception as e:
            # Fallback to basic evaluation on structured output failure
            print(f"Structured output failed for {self.persona}: {e}")
            basic_response = await self._fallback_evaluation(prompt)
            return JudicialOpinion(
                judge="Prosecutor",  # Use Prosecutor as default
                criterion_id=criterion["id"],
                score=self._extract_score_from_fallback(basic_response),
                argument=basic_response[:500],  # Truncate for safety
                cited_evidence=["fallback_evidence"]
            )
    
    async def _fallback_evaluation(self, prompt: str) -> str:
        """Fallback evaluation when structured output fails."""
        response = await self.llm.ainvoke(prompt)
        if hasattr(response, 'content'):
            return str(getattr(response, 'content', str(response)))
        return str(getattr(response, 'content', str(response)))
    
    def _extract_score_from_fallback(self, response: str) -> int:
        """Extract score from fallback response (conservative approach)."""
        try:
            # Look for numeric scores in response
            for word in response.split():
                if word.isdigit():
                    score = int(word)
                    if 1 <= score <= 5:
                        return score
            return 3  # Default neutral score
        except:
            return 3


class ProsecutorAgent(JudgeAgent):
    """Adversarial prosecutor agent - finds flaws and security issues."""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        super().__init__("Prosecutor", model_name)
    
    def _build_prompt(self, criterion: Dict[str, Any], evidence: str) -> str:
        return f"""You are the PROSECUTOR evaluating code quality. Your mission is to find security flaws, gaps in implementation, and signs of laziness.

RUBRIC CRITERION TO EVALUATE:
{criterion}

EVIDENCE TO EVALUATE:
{evidence}

PROSECUTOR EVALUATION PRIORITIES:
1. Find security vulnerabilities and weak points
2. Identify missing safety checks and error handling
3. Detect shortcuts, hacks, or poor practices
4. Spot performance bottlenecks
5. Identify architectural flaws
6. Find documentation gaps

Remember: Be strict and skeptical. Don't give credit for effort - evaluate based on actual security and reliability.

Output ONLY the structured JSON object matching JudicialOpinion schema."""


class DefenseAgent(JudgeAgent):
    """Benevolent defense agent - rewards effort and creative solutions."""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        super().__init__("Defense", model_name)
    
    def _build_prompt(self, criterion: Dict[str, Any], evidence: str) -> str:
        return f"""You are the DEFENSE attorney evaluating code quality. Your mission is to recognize effort, creativity, and positive attributes.

RUBRIC CRITERION TO EVALUATE:
{criterion}

EVIDENCE TO EVALUATE:
{evidence}

DEFENSE EVALUATION PRIORITIES:
1. Recognize clever solutions and innovative approaches
2. Reward thoroughness and attention to detail
3. Appreciate educational or explanatory content
4. Acknowledge defensive programming practices
5. Credit proper testing and validation
6. Recognize user experience considerations

Remember: Be generous and encouraging. Look for what's working well rather than what's missing.

Output ONLY the structured JSON object matching JudicialOpinion schema."""


class TechLeadAgent(JudgeAgent):
    """Pragmatic tech lead agent - evaluates viability and maintainability."""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        super().__init__("TechLead", model_name)
    
    def _build_prompt(self, criterion: Dict[str, Any], evidence: str) -> str:
        return f"""You are the TECH LEAD evaluating code quality. Your mission is to assess maintainability, scalability, and production readiness.

RUBRIC CRITERION TO EVALUATE:
{criterion}

EVIDENCE TO EVALUATE:
{evidence}

TECH LEAD EVALUATION PRIORITIES:
1. Assess code organization and modularity
2. Evaluate maintainability and extensibility
3. Assess error handling and edge case coverage
4. Consider performance implications and scalability
5. Look for proper separation of concerns
6. Evaluate documentation quality for future developers

Remember: Be pragmatic and objective. Ignore "vibe" and "struggle" and focus on whether the system would work reliably in production.

Output ONLY the structured JSON object matching JudicialOpinion schema."""


class JudgeAgents:
    """Container for all judge agents with initialization and access methods."""
    
    def __init__(self):
        self.prosecutor = ProsecutorAgent()
        self.defense = DefenseAgent()
        self.tech_lead = TechLeadAgent()
    
    def get_agent(self, judge_type: str) -> Optional[JudgeAgent]:
        """Get specific judge agent by type."""
        agents = {
            "Prosecutor": self.prosecutor,
            "Defense": self.defense, 
            "TechLead": self.tech_lead
        }
        return agents.get(judge_type)
    
    async def evaluate_with_all_judges(self, criterion: Dict[str, Any], evidence: str) -> list:
        """Evaluate a criterion with all three judges in parallel."""
        import asyncio
        
        tasks = [
            self.prosecutor.evaluate(criterion, evidence),
            self.defense.evaluate(criterion, evidence),
            self.tech_lead.evaluate(criterion, evidence)
        ]
        
        # Execute all evaluations concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions and return valid opinions
        opinions = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Judge evaluation failed: {result}")
                # Create fallback opinion
                opinions.append(JudicialOpinion(
                    judge="Prosecutor",
                    criterion_id=criterion["id"],
                    score=3,
                    argument="Evaluation failed due to error",
                    cited_evidence=[]
                ))
            else:
                opinions.append(result)
        
        return opinions
        

# Convenience function for getting judge agents
judge_agents = JudgeAgents()