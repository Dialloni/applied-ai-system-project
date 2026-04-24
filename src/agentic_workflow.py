"""
Agentic Workflow for Music Recommendations.

This module implements an AI agent that can:
1. Analyze user preferences
2. Generate recommendations
3. Evaluate recommendation quality
4. Refine recommendations based on feedback
5. Self-correct and improve through iteration

The agent follows a plan-act-evaluate loop for autonomous refinement.
"""

from typing import List, Dict, Tuple, Optional
from enum import Enum
import json


class AgentState(Enum):
    """States the recommendation agent can be in."""
    ANALYZING = "analyzing"
    GENERATING = "generating"
    EVALUATING = "evaluating"
    REFINING = "refining"
    COMPLETE = "complete"


class RecommendationAgent:
    """
    Agentic AI system that autonomously improves recommendations through iteration.
    
    Workflow:
    1. ANALYZE: Understand user preferences deeply
    2. GENERATE: Create initial recommendations
    3. EVALUATE: Assess recommendation quality
    4. REFINE: Improve based on quality metrics
    5. COMPLETE: Return final recommendations with confidence scores
    """

    def __init__(self, recommender, rag_system=None):
        """
        Initialize the agent.
        
        Args:
            recommender: The base recommender system
            rag_system: Optional RAG system for LLM-enhanced explanations
        """
        self.recommender = recommender
        self.rag_system = rag_system
        self.state = AgentState.ANALYZING
        self.iteration_count = 0
        self.max_iterations = 3
        self.action_log: List[Dict] = []
        self.quality_scores: List[float] = []

    def plan(self, user_prefs: Dict) -> Dict:
        """
        PLAN: Analyze user preferences and create a recommendation strategy.
        
        Args:
            user_prefs: User preference dictionary
            
        Returns:
            Strategy dictionary with analysis and approach
        """
        strategy = {
            "step": "plan",
            "user_profile": user_prefs,
            "constraints": [],
            "scoring_mode": "default",
            "diversity_focus": False,
        }

        # Analyze preference constraints
        if user_prefs.get("energy", 0.5) > 0.8:
            strategy["constraints"].append("high_energy_required")
        elif user_prefs.get("energy", 0.5) < 0.4:
            strategy["constraints"].append("low_energy_preferred")

        if user_prefs.get("likes_acoustic"):
            strategy["constraints"].append("prefer_acoustic")
        else:
            strategy["constraints"].append("prefer_electronic")

        # Determine scoring strategy
        mood = user_prefs.get("mood", "").lower()
        if "intense" in mood or "aggressive" in mood:
            strategy["scoring_mode"] = "energy_focused"
        elif "chill" in mood or "relaxed" in mood:
            strategy["scoring_mode"] = "mood_first"

        strategy["num_recommendations"] = 5
        strategy["diversity_penalty"] = len(strategy["constraints"]) > 2

        self.action_log.append(strategy)
        return strategy

    def act(
        self,
        user_prefs: Dict,
        strategy: Dict,
        songs: List[Dict],
    ) -> List[Tuple[Dict, float, List[str]]]:
        """
        ACT: Generate recommendations based on the strategy.
        
        Args:
            user_prefs: User preferences
            strategy: Strategy from planning phase
            songs: Available songs
            
        Returns:
            List of (song, score, reasons) tuples
        """
        from .recommender import recommend_songs

        self.state = AgentState.GENERATING
        
        recommendations = recommend_songs(
            user_prefs=user_prefs,
            songs=songs,
            k=strategy.get("num_recommendations", 5),
            mode=strategy.get("scoring_mode", "default"),
            diversity_penalty=strategy.get("diversity_penalty", False),
        )

        action = {
            "step": "act",
            "strategy_applied": strategy,
            "recommendations_generated": len(recommendations),
            "top_score": recommendations[0][1] if recommendations else 0,
        }
        self.action_log.append(action)

        return recommendations

    def evaluate(
        self,
        recommendations: List[Tuple[Dict, float, List[str]]],
        user_prefs: Dict,
    ) -> Tuple[float, Dict]:
        """
        EVALUATE: Assess the quality of recommendations.
        
        Args:
            recommendations: Generated recommendations
            user_prefs: User preferences
            
        Returns:
            (quality_score, evaluation_dict) tuple
        """
        self.state = AgentState.EVALUATING
        
        if not recommendations:
            return 0.0, {"error": "No recommendations generated"}

        quality_metrics = {
            "genre_match_rate": 0.0,
            "mood_match_rate": 0.0,
            "energy_alignment": 0.0,
            "diversity_score": 0.0,
            "avg_score": 0.0,
        }

        # Genre and mood match rates
        genre_matches = sum(
            1 for song, _, _ in recommendations
            if song.get("genre") == user_prefs.get("genre")
        )
        quality_metrics["genre_match_rate"] = genre_matches / len(recommendations)

        mood_matches = sum(
            1 for song, _, _ in recommendations
            if song.get("mood") == user_prefs.get("mood")
        )
        quality_metrics["mood_match_rate"] = mood_matches / len(recommendations)

        # Energy alignment
        target_energy = user_prefs.get("energy", 0.5)
        energy_diffs = [
            abs(song["energy"] - target_energy)
            for song, _, _ in recommendations
        ]
        quality_metrics["energy_alignment"] = 1.0 - (
            sum(energy_diffs) / len(energy_diffs)
        )

        # Diversity (artist and genre diversity)
        artists = set(song["artist"] for song, _, _ in recommendations)
        genres = set(song["genre"] for song, _, _ in recommendations)
        quality_metrics["diversity_score"] = (
            len(artists) / len(recommendations) * 0.5 +
            len(genres) / len(recommendations) * 0.5
        )

        # Average recommendation score
        avg_score = sum(score for _, score, _ in recommendations) / len(
            recommendations
        )
        quality_metrics["avg_score"] = avg_score

        # Overall quality score (weighted)
        quality_score = (
            quality_metrics["genre_match_rate"] * 0.25 +
            quality_metrics["mood_match_rate"] * 0.25 +
            quality_metrics["energy_alignment"] * 0.20 +
            quality_metrics["diversity_score"] * 0.15 +
            min(avg_score / 4.5, 1.0) * 0.15  # Normalize avg score
        )

        self.quality_scores.append(quality_score)

        evaluation = {
            "step": "evaluate",
            "iteration": self.iteration_count,
            "quality_score": round(quality_score, 2),
            "metrics": {k: round(v, 2) for k, v in quality_metrics.items()},
            "pass_threshold": quality_score > 0.65,
        }
        self.action_log.append(evaluation)

        return quality_score, evaluation

    def refine(
        self,
        user_prefs: Dict,
        quality_score: float,
        strategy: Dict,
    ) -> Optional[Dict]:
        """
        REFINE: Adjust strategy based on evaluation.
        
        Args:
            user_prefs: User preferences
            quality_score: Quality score from evaluation
            strategy: Current strategy
            
        Returns:
            Refined strategy or None if no refinement needed
        """
        if quality_score > 0.65 or self.iteration_count >= self.max_iterations:
            return None

        self.state = AgentState.REFINING
        refined_strategy = strategy.copy()

        if quality_score < 0.4:
            # Low quality: switch to different scoring mode
            modes = ["default", "mood_first", "energy_focused"]
            current_idx = modes.index(strategy.get("scoring_mode", "default"))
            refined_strategy["scoring_mode"] = modes[(current_idx + 1) % len(modes)]
            refined_strategy["diversity_penalty"] = True

        elif quality_score < 0.6:
            # Medium quality: increase diversity
            refined_strategy["diversity_penalty"] = True

        refinement = {
            "step": "refine",
            "iteration": self.iteration_count,
            "quality_score": quality_score,
            "changes": {
                "old_mode": strategy.get("scoring_mode"),
                "new_mode": refined_strategy.get("scoring_mode"),
                "old_diversity": strategy.get("diversity_penalty"),
                "new_diversity": refined_strategy.get("diversity_penalty"),
            },
        }
        self.action_log.append(refinement)

        return refined_strategy

    def run(
        self,
        user_prefs: Dict,
        songs: List[Dict],
    ) -> Tuple[List[Tuple[Dict, float, List[str]]], Dict]:
        """
        Execute the full agentic workflow: plan → act → evaluate → refine (loop).
        
        Args:
            user_prefs: User preferences
            songs: Available songs
            
        Returns:
            (final_recommendations, workflow_summary) tuple
        """
        self.iteration_count = 0
        best_recommendations = None
        best_quality = 0.0

        while self.iteration_count < self.max_iterations:
            # PLAN
            strategy = self.plan(user_prefs)

            # ACT
            recommendations = self.act(user_prefs, strategy, songs)

            # EVALUATE
            quality_score, evaluation = self.evaluate(recommendations, user_prefs)

            # Store best result
            if quality_score > best_quality:
                best_quality = quality_score
                best_recommendations = recommendations

            # Check if quality is acceptable
            if evaluation.get("pass_threshold"):
                self.state = AgentState.COMPLETE
                break

            # REFINE
            refined_strategy = self.refine(user_prefs, quality_score, strategy)
            if refined_strategy is None:
                self.state = AgentState.COMPLETE
                break

            self.iteration_count += 1

        self.state = AgentState.COMPLETE

        summary = {
            "total_iterations": self.iteration_count,
            "final_quality_score": round(best_quality, 2),
            "quality_improvement": (
                round(self.quality_scores[-1] - self.quality_scores[0], 2)
                if len(self.quality_scores) > 1
                else 0.0
            ),
            "workflow_log": self.action_log,
        }

        return best_recommendations or [], summary

    def export_workflow(self) -> str:
        """Export the agent's workflow and decisions as JSON."""
        return json.dumps(
            {
                "final_state": self.state.value,
                "iterations": self.iteration_count,
                "quality_scores": self.quality_scores,
                "action_log": self.action_log,
            },
            indent=2,
        )
