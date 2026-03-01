"""
Chief Justice Synthesis Engine - Deterministic conflict resolution.
"""

import json
from typing import Dict, List, Any

from src.state import AgentState, JudicialOpinion, CriterionResult, AuditReport


class ChiefJustice:
    """Synthesizes judge opinions using deterministic rules."""
    
    def __init__(self):
        self.synthesis_rules = {
            "security_override": "Confirmed security flaws cap the total score at 3",
            "fact_supremacy": "Forensic evidence overrules judicial opinion",
            "functionality_weight": "Tech Lead architecture assessment carries highest weight",
            "dissent_requirement": "Score variance > 2 requires dissent explanation",
            "variance_re_evaluation": "High variance triggers evidence re-evaluation"
        }
    
    async def chief_justice_node(self, state: AgentState) -> Dict[str, Any]:
        """Chief Justice node that synthesizes all judge opinions."""
        
        print("[ChiefJustice] Synthesizing judge opinions...")
        
        opinions_by_criterion = state.get("opinions_by_criterion", {})
        evidences = state.get("evidences", {})
        rubric_dimensions = state.get("rubric_dimensions", [])
        
        criterion_results = []
        total_score = 0
        
        # Process each criterion
        for dimension in rubric_dimensions:
            criterion_id = dimension["id"]
            opinions = opinions_by_criterion.get(criterion_id, [])
            
            # Separate opinions by judge type
            prosecutor_ops = [o for o in opinions if o["judge"] == "Prosecutor"]
            defense_ops = [o for o in opinions if o["judge"] == "Defense"]
            tech_lead_ops = [o for o in opinions if o["judge"] == "TechLead"]
            
            # Ensure we have exactly one opinion per judge type
            prosecutor = prosecutor_ops[0] if prosecutor_ops else JudicialOpinion(
                judge="Prosecutor", criterion_id=criterion_id, score=3, 
                argument="No prosecutor opinion available", cited_evidence=[]
            )
            defense = defense_ops[0] if defense_ops else JudicialOpinion(
                judge="Defense", criterion_id=criterion_id, score=3,
                argument="No defense opinion available", cited_evidence=[]
            )
            tech_lead = tech_lead_ops[0] if tech_lead_ops else JudicialOpinion(
                judge="TechLead", criterion_id=criterion_id, score=3,
                argument="No tech lead opinion available", cited_evidence=[]
            )
            
            # Aggregate opinions for this criterion
            result = self._synthesize_criterion(
                dimension, 
                [prosecutor, defense, tech_lead], 
                evidences
            )
            criterion_results.append(result)
            total_score += result.final_score
        
        # Calculate overall score
        overall_score = total_score / len(criterion_results) if criterion_results else 3.0
        
        # Generate final report
        audit_report = self._generate_report(
            state.get("repo_url", "unknown"),
            criterion_results,
            overall_score
        )
        
        return {
            **state,
            "criteria_results": criterion_results,
            "overall_score": overall_score,
            "final_report": audit_report,
            "synthesis_complete": True
        }
    
    def _synthesize_criterion(self, dimension: Dict[str, Any], 
                            opinions: List[JudicialOpinion], 
                            evidences: Dict[str, List]) -> CriterionResult:
        """Synthesize opinions for a single criterion using deterministic rules."""
        
        prosecutor, defense, tech_lead = opinions[0], opinions[1], opinions[2]
        dimension_id = dimension["id"]
        dimension_name = dimension["name"]
        
        # Extract scores from JudicialOpinion objects
        prosecutor_score = prosecutor.score
        defense_score = defense.score
        tech_lead_score = tech_lead.score
        
        # Apply synthesis rules
        final_score, dissent_summary, remediation = self._apply_synthesis_rules(
            dimension_id, prosecutor, defense, tech_lead, evidences
        )
        
        return CriterionResult(
            dimension_id=dimension_id,
            dimension_name=dimension_name,
            final_score=final_score,
            judge_opinions=opinions,
            dissent_summary=dissent_summary,
            remediation=remediation
        )
    
    def _apply_synthesis_rules(self, criterion_id: str, prosecutor: JudicialOpinion,
                              defense: JudicialOpinion, tech_lead: JudicialOpinion,
                              evidences: Dict[str, List]) -> tuple:
        """Apply deterministic synthesis rules to resolve conflicts."""
        
        # Extract scores from JudicialOpinion objects
        p_score = prosecutor.score
        d_score = defense.score
        t_score = tech_lead.score
        
        # Rule 1: Security Override
        # If Prosecutor identifies security flaws, cap at 3 regardless of Defense
        if self._has_security_violation(prosecutor):
            final_score = min(3, (p_score + d_score + t_score) // 3)
            dissent_summary = (f"Security override applied: Prosecutor identified "
                             f"critical security violation ({p_score})"
                            )
            remediation = (f"Fix security violation identified by Prosecutor: "
                         f"{prosecutor.argument}"
                        )
            return final_score, dissent_summary, remediation
        
        # Rule 2: Fact Supremacy
        # If Defense claims features that don't exist in evidence, reduce their weight
        if self._defense_claims_missing_facts(defense, evidences):
            # Reduce Defense score influence
            weighted_score = (p_score * 0.4 + d_score * 0.2 + t_score * 0.4)
            final_score = max(1, min(5, round(weighted_score)))
            dissent_summary = (f"Fact supremacy applied: Defense claimed missing features "
                             f"({d_score} vs reality)"
                            )
            remediation = (f"Implement missing features claimed by Defense or "
                         f"remove false assertions"
                        )
            return final_score, dissent_summary, remediation
        
        # Rule 3: Functionality Weight
        # Tech Lead architectural assessment carries higher weight
        if self._tech_lead_confirms_architecture(tech_lead):
            weighted_score = (p_score * 0.3 + d_score * 0.2 + t_score * 0.5)
            final_score = max(1, min(5, round(weighted_score)))
            dissent_summary = f"Functionality weight: Tech Lead assessment prioritized"
            remediation = (f"Leverage Tech Lead's architectural insights for improvement"
                        )
            return final_score, dissent_summary, remediation
        
        # Rule 4: Variance Re-evaluation
        # High variance triggers conservative scoring
        variance = max(abs(p_score - d_score), abs(p_score - t_score), abs(d_score - t_score))
        if variance > 2:
            # Conservative approach - take the minimum of the two closest scores
            scores = sorted([p_score, d_score, t_score])
            final_score = scores[1]  # Median score
            dissent_summary = (f"High variance re-evaluation: Scores range {scores[0]}-{scores[2]}. "
                             f"Conservative median score applied."
                            )
            remediation = (f"Address major disagreements between judges "
                         f"to achieve consensus"
                        )
            return final_score, dissent_summary, remediation
        
        # Default: Weighted average with deliberation
        weighted_score = (p_score * 0.35 + d_score * 0.3 + t_score * 0.35)
        final_score = max(1, min(5, round(weighted_score)))
        
        # Rule 5: Dissent Requirement
        if variance > 1:
            dissent_summary = self._generate_dissent_summary(prosecutor, defense, tech_lead)
            remediation = f"Address disagreement between {self._identify_dissenters(prosecutor, defense, tech_lead)}"
        else:
            dissent_summary = None
            remediation = "Minor disagreements present - focus on incremental improvements"
        
        return final_score, dissent_summary, remediation
    
    def _has_security_violation(self, prosecutor: JudicialOpinion) -> bool:
        """Check if Prosecutor identified a security violation."""
        argument = prosecutor.argument.lower()
        security_keywords = ["security", "vulnerability", "unsafe", "injection", 
                           "malicious", "exploit", "dangerous", "risk"]
        return any(keyword in argument for keyword in security_keywords)
    
    def _defense_claims_missing_facts(self, defense: JudicialOpinion, 
                                    evidences: Dict[str, List]) -> bool:
        """Check if Defense claims features not supported by evidence."""
        argument = defense.argument.lower()
        # Check if defense claims deep understanding but evidence is sparse
        deep_keywords = ["deep", "metacognition", "sophisticated", "advanced", "innovative"]
        has_deep_claims = any(keyword in argument for keyword in deep_keywords)
        
        # Check if evidence is minimal
        total_evidence_pieces = sum(len(items) for items in evidences.values())
        return has_deep_claims and total_evidence_pieces < 5
    
    def _tech_lead_confirms_architecture(self, tech_lead: JudicialOpinion) -> bool:
        """Check if Tech Lead confirms architectural soundness."""
        argument = tech_lead.argument.lower()
        arch_keywords = ["architectural", "modular", "scalable", "maintainable", 
                       "well-structured", "proper", "sound"]
        return any(keyword in argument for keyword in arch_keywords)
    
    def _generate_dissent_summary(self, prosecutor: JudicialOpinion, 
                                defense: JudicialOpinion, 
                                tech_lead: JudicialOpinion) -> str:
        """Generate summary of judicial disagreements."""
        p_score = prosecutor.score
        d_score = defense.score
        t_score = tech_lead.score
        
        summary = f"Prosecutor scored {p_score}, Defense scored {d_score}, Tech Lead scored {t_score}. "
        
        if p_score < d_score:
            summary += f"Prosecutor was more critical than Defense"
        elif p_score > d_score:
            summary += f"Defense was more generous than Prosecutor"
        
        if t_score != (p_score + d_score) // 2:
            summary += f", Tech Lead provided balanced assessment"
        
        return summary
    
    def _identify_dissenters(self, prosecutor: JudicialOpinion, 
                           defense: JudicialOpinion, 
                           tech_lead: JudicialOpinion) -> str:
        """Identify the judges with the strongest disagreement."""
        p_score = prosecutor.score
        d_score = defense.score
        t_score = tech_lead.score
        
        if abs(p_score - d_score) > abs(p_score - t_score):
            return "Prosecutor and Defense"
        else:
            return "most dissenting judges"
    
    def _generate_report(self, repo_url: str, criteria: List[CriterionResult], 
                       overall_score: float) -> AuditReport:
        """Generate the final audit report."""
        
        # Generate executive summary
        if overall_score >= 4.0:
            exec_summary = f"Excellent audit results ({overall_score:.1f}/5.0). Strong implementation with minor areas for improvement."
        elif overall_score >= 3.0:
            exec_summary = f"Good audit results ({overall_score:.1f}/5.0). Solid foundation with several improvement opportunities."
        else:
            exec_summary = f"Needs improvement ({overall_score:.1f}/5.0). Significant architectural and implementation issues identified."
        
        # Generate remediation plan
        remediation_plan = self._generate_remediation_plan(criteria)
        
        return AuditReport(
            repo_url=repo_url,
            executive_summary=exec_summary,
            overall_score=overall_score,
            criteria=criteria,
            remediation_plan=remediation_plan
        )
    
    def _generate_remediation_plan(self, criteria: List[CriterionResult]) -> str:
        """Generate comprehensive remediation plan."""
        
        plan_sections = ["# Remediation Plan\n"]
        
        low_scores = [c for c in criteria if c.final_score < 3]
        medium_scores = [c for c in criteria if 3 <= c.final_score < 4]
        high_scores = [c for c in criteria if c.final_score >= 4]
        
        if low_scores:
            plan_sections.append("## Critical Issues (Score < 3)\n")
            for criterion in low_scores:
                plan_sections.append(f"### {criterion.dimension_name}\n")
                plan_sections.append(f"**Final Score:** {criterion.final_score}/5\n")
                plan_sections.append(f"**Action:** {criterion.remediation}\n")
        
        if medium_scores:
            plan_sections.append("\n## Improvement Opportunities (Score 3-4)\n")
            for criterion in medium_scores:
                plan_sections.append(f"### {criterion.dimension_name}\n")
                plan_sections.append(f"**Final Score:** {criterion.final_score}/5\n")
                plan_sections.append(f"**Action:** {criterion.remediation}\n")
        
        if high_scores:
            plan_sections.append("\n## Strengths (Score >= 4)\n")
            for criterion in high_scores:
                plan_sections.append(f"### {criterion.dimension_name}\n")
                plan_sections.append(f"**Final Score:** {criterion.final_score}/5\n")
                plan_sections.append(f"**Continue:** Maintain these strengths\n")
        
        return "\n".join(plan_sections)


# Convenience instance
chief_justice = ChiefJustice()