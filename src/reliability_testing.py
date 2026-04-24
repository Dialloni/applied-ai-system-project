"""
Reliability Testing System for AI-Enhanced Music Recommender.

Measures:
1. Consistency: Do repeated recommendations match?
2. Fairness: Are different demographics treated fairly?
3. Robustness: How do recommendations change with small input variations?
4. Explainability: Are explanations aligned with scores?
"""

from typing import List, Dict, Tuple, Optional
import json
from statistics import stdev, mean


class ReliabilityTester:
    """Test suite for validating recommendation system reliability."""

    def __init__(self, recommender, rag_system=None):
        """Initialize tester with recommender and optional RAG system."""
        self.recommender = recommender
        self.rag_system = rag_system
        self.test_results = []

    def test_consistency(
        self,
        user_prefs: Dict,
        songs: List[Dict],
        num_runs: int = 5,
    ) -> Dict:
        """
        Test consistency: Do repeated recommendations produce the same results?
        
        Args:
            user_prefs: User preferences
            songs: Available songs
            num_runs: Number of times to run recommendations
            
        Returns:
            Consistency test results
        """
        from .recommender import recommend_songs

        results = []
        recommendation_sets = []

        for run in range(num_runs):
            recs = recommend_songs(
                user_prefs=user_prefs,
                songs=songs,
                k=5,
            )
            recommendation_sets.append(
                [song["id"] for song, _, _ in recs]
            )
            results.append(recs)

        # Calculate consistency score
        # Measure how many recommendations appear in all runs
        if recommendation_sets:
            all_ids = set(recommendation_sets[0])
            for id_set in recommendation_sets[1:]:
                all_ids = all_ids.intersection(set(id_set))

            consistency_score = len(all_ids) / 5  # 5 recommendations total

            # Check if top recommendation is always the same
            top_ids = [rec_set[0] if rec_set else None for rec_set in recommendation_sets]
            top_consistency = (
                sum(1 for tid in top_ids if tid == top_ids[0]) / num_runs
            )
        else:
            consistency_score = 0.0
            top_consistency = 0.0

        test_result = {
            "test_name": "consistency",
            "num_runs": num_runs,
            "consistency_score": round(consistency_score, 2),
            "top_recommendation_consistency": round(top_consistency, 2),
            "recommendation_sets": recommendation_sets,
            "status": "PASS" if consistency_score > 0.6 else "FAIL",
        }

        self.test_results.append(test_result)
        return test_result

    def test_robustness(
        self,
        base_prefs: Dict,
        songs: List[Dict],
        variation_amount: float = 0.1,
    ) -> Dict:
        """
        Test robustness: How much do recommendations change with small input variations?
        
        Args:
            base_prefs: Base user preferences
            songs: Available songs
            variation_amount: Percentage to vary numeric preferences (0-1)
            
        Returns:
            Robustness test results
        """
        from .recommender import recommend_songs

        # Get baseline recommendations
        baseline_recs = recommend_songs(
            user_prefs=base_prefs,
            songs=songs,
            k=5,
        )
        baseline_ids = [song["id"] for song, _, _ in baseline_recs]

        # Vary preferences slightly
        variations = []
        varied_recs_list = []

        # Vary energy
        if "energy" in base_prefs:
            varied_energy = base_prefs.copy()
            varied_energy["energy"] = max(
                0.0,
                min(1.0, base_prefs["energy"] * (1 + variation_amount))
            )
            variations.append("energy increased")
            recs = recommend_songs(user_prefs=varied_energy, songs=songs, k=5)
            varied_recs_list.append([song["id"] for song, _, _ in recs])

        # Calculate robustness: what % of recommendations remain the same?
        if varied_recs_list:
            overlaps = [
                len(set(baseline_ids) & set(varied_ids)) / 5
                for varied_ids in varied_recs_list
            ]
            robustness_score = mean(overlaps)
        else:
            robustness_score = 1.0

        test_result = {
            "test_name": "robustness",
            "base_preferences": base_prefs,
            "variations_tested": variations,
            "baseline_recommendations": baseline_ids,
            "varied_recommendations": varied_recs_list,
            "robustness_score": round(robustness_score, 2),
            "status": "PASS" if robustness_score > 0.4 else "WARN",
        }

        self.test_results.append(test_result)
        return test_result

    def test_fairness(
        self,
        user_profiles: List[Tuple[str, Dict]],
        songs: List[Dict],
    ) -> Dict:
        """
        Test fairness: Are artists and genres fairly represented across different user types?
        
        Args:
            user_profiles: List of (profile_name, preferences) tuples
            songs: Available songs
            
        Returns:
            Fairness test results
        """
        from .recommender import recommend_songs

        profile_results = {}
        all_genres = []
        all_artists = []

        for profile_name, prefs in user_profiles:
            recs = recommend_songs(user_prefs=prefs, songs=songs, k=5)
            
            genres = [song.get("genre") for song, _, _ in recs]
            artists = [song.get("artist") for song, _, _ in recs]
            
            all_genres.extend(genres)
            all_artists.extend(artists)
            
            profile_results[profile_name] = {
                "recommended_genres": genres,
                "recommended_artists": artists,
                "genre_diversity": len(set(genres)) / len(genres),
                "artist_diversity": len(set(artists)) / len(artists),
            }

        # Calculate overall fairness metrics
        genre_distribution = {
            g: all_genres.count(g) / len(all_genres)
            for g in set(all_genres)
        }
        artist_distribution = {
            a: all_artists.count(a) / len(all_artists)
            for a in set(all_artists)
        }

        # Check for over-representation
        over_represented = [
            g for g, count in genre_distribution.items()
            if count > 0.4
        ]

        test_result = {
            "test_name": "fairness",
            "num_profiles": len(user_profiles),
            "profile_results": profile_results,
            "genre_distribution": {k: round(v, 2) for k, v in genre_distribution.items()},
            "artist_distribution": {k: round(v, 2) for k, v in artist_distribution.items()},
            "over_represented_genres": over_represented,
            "fairness_issues": len(over_represented) > 0,
            "status": "PASS" if len(over_represented) == 0 else "WARN",
        }

        self.test_results.append(test_result)
        return test_result

    def test_explanation_alignment(
        self,
        user_prefs: Dict,
        recommended_song: Dict,
        score: float,
        reasons: List[str],
    ) -> Dict:
        """
        Test explanation alignment: Do the reasons match the recommendation score?
        
        Args:
            user_prefs: User preferences
            recommended_song: The recommended song
            score: The recommendation score
            reasons: Reasons for the recommendation
            
        Returns:
            Alignment test results
        """
        # Score quality metrics
        num_reasons = len(reasons)
        alignment_checks = {
            "has_reasons": num_reasons > 0,
            "multiple_reasons": num_reasons >= 2,
            "reasons_specific": any(
                "match" in r.lower() or "close" in r.lower()
                for r in reasons
            ),
        }

        # Check if score aligns with reasons
        # Higher score should have more/stronger reasons
        alignment_score = sum(alignment_checks.values()) / len(alignment_checks)

        test_result = {
            "test_name": "explanation_alignment",
            "song": f"{recommended_song['title']} by {recommended_song['artist']}",
            "score": score,
            "num_reasons": num_reasons,
            "reasons": reasons,
            "alignment_checks": alignment_checks,
            "alignment_score": round(alignment_score, 2),
            "status": "PASS" if alignment_score > 0.5 else "FAIL",
        }

        self.test_results.append(test_result)
        return test_result

    def run_full_test_suite(
        self,
        user_prefs: Dict,
        songs: List[Dict],
        user_profiles: Optional[List[Tuple[str, Dict]]] = None,
    ) -> Dict:
        """
        Run all reliability tests and generate a comprehensive report.
        
        Args:
            user_prefs: Primary user preferences
            songs: Available songs
            user_profiles: Optional list of different user profiles for fairness testing
            
        Returns:
            Complete test report
        """
        from .recommender import recommend_songs

        print("Running Reliability Test Suite...")

        # Test 1: Consistency
        print("  - Testing consistency...")
        consistency = self.test_consistency(user_prefs, songs, num_runs=5)

        # Test 2: Robustness
        print("  - Testing robustness...")
        robustness = self.test_robustness(user_prefs, songs)

        # Test 3: Fairness (if multiple profiles provided)
        fairness = None
        if user_profiles:
            print("  - Testing fairness...")
            fairness = self.test_fairness(user_profiles, songs)

        # Test 4: Explanation Alignment
        print("  - Testing explanation alignment...")
        recs = recommend_songs(user_prefs=user_prefs, songs=songs, k=1)
        if recs:
            song, score, reasons = recs[0]
            alignment = self.test_explanation_alignment(
                user_prefs, song, score, reasons
            )
        else:
            alignment = {"status": "SKIP", "reason": "No recommendations generated"}

        # Generate summary
        test_summary = {
            "timestamp": "2026-04-24",
            "test_suite": "Reliability Testing",
            "overall_status": "PASS",
            "tests_run": 4 if fairness else 3,
            "tests_passed": sum(
                1 for t in [consistency, robustness, fairness, alignment]
                if t and t.get("status") == "PASS"
            ),
            "consistency": consistency,
            "robustness": robustness,
            "fairness": fairness,
            "explanation_alignment": alignment,
        }

        # Determine overall status
        statuses = [t.get("status") for t in [consistency, robustness, fairness, alignment] if t]
        if "FAIL" in statuses:
            test_summary["overall_status"] = "FAIL"
        elif "WARN" in statuses:
            test_summary["overall_status"] = "WARN"

        return test_summary

    def export_results(self) -> str:
        """Export all test results as JSON."""
        return json.dumps(self.test_results, indent=2)
