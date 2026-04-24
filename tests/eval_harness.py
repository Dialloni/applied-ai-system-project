"""
Evaluation Harness — Extra Credit (Test Harness Feature)

Runs VibeFinder against 6 predefined user profiles and prints a
pass/fail summary with confidence ratings and quality metrics.

Usage:
    python tests/eval_harness.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.recommender import load_songs, recommend_songs
from src.agentic_workflow import RecommendationAgent, AgentState
from src.recommender import Recommender

SONGS = load_songs("data/songs.csv")

# Each test case defines: user preferences, expected genres in top-3, min quality score
TEST_CASES = [
    {
        "name": "Chill Lofi Student",
        "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.38, "likes_acoustic": True},
        "expected_genres": ["lofi"],
        "min_top_score": 4.0,
        "description": "Lofi fan should get lofi songs at top",
    },
    {
        "name": "High-Energy Pop Fan",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.90, "target_valence": 0.85},
        "expected_genres": ["pop"],
        "min_top_score": 3.5,
        "description": "Pop fan should get pop songs with high scores",
    },
    {
        "name": "Deep Intense Rock",
        "prefs": {"genre": "rock", "mood": "intense", "energy": 0.92},
        "expected_genres": ["rock"],
        "min_top_score": 3.0,
        "description": "Rock fan should get rock as top result",
    },
    {
        "name": "Jazz Relaxed Listener",
        "prefs": {"genre": "jazz", "mood": "relaxed", "energy": 0.30, "likes_acoustic": True},
        "expected_genres": ["jazz"],
        "min_top_score": 2.0,
        "description": "Jazz fan should get jazz genre match",
    },
    {
        "name": "Adversarial: Missing Genre (Reggae)",
        "prefs": {"genre": "reggae", "mood": "relaxed", "energy": 0.60},
        "expected_genres": [],  # no reggae in catalog — expect 0 genre matches (system should still return something)
        "min_top_score": 0.0,
        "description": "Missing genre — expect 0 genre matches but system should not crash",
        "expect_zero_genre_matches": True,
    },
    {
        "name": "Mood Tags: Peaceful + Lofi",
        "prefs": {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.35,
            "likes_acoustic": True,
            "mood_tags": ["peaceful", "meditative"],
        },
        "expected_genres": ["lofi"],
        "min_top_score": 4.5,
        "description": "Mood tags should boost songs with matching tags",
    },
]


def run_test(case: dict, songs: list) -> dict:
    """Run one test case. Returns result dict with pass/fail and metrics."""
    prefs = case["prefs"]
    recs = recommend_songs(prefs, songs, k=5)

    top_song, top_score, top_reasons = recs[0]
    top_genres = [r[0]["genre"] for r in recs[:3]]
    genre_matches = sum(1 for g in top_genres if g in case.get("expected_genres", []))

    # Pass conditions
    score_ok = top_score >= case["min_top_score"]

    if case.get("expect_zero_genre_matches"):
        genre_ok = genre_matches == 0
    else:
        genre_ok = genre_matches >= 1

    passed = score_ok and genre_ok

    # Confidence rating: normalized top score (max possible ~5.5)
    confidence = round(min(top_score / 5.5, 1.0), 2)

    # Run agent for quality score
    agent = RecommendationAgent(Recommender([]))
    quality_score, evaluation = agent.evaluate(recs, prefs)

    return {
        "name": case["name"],
        "passed": passed,
        "top_song": f"{top_song['title']} by {top_song['artist']}",
        "top_genre": top_song["genre"],
        "top_score": top_score,
        "confidence": confidence,
        "quality_score": round(quality_score, 2),
        "genre_matches_in_top3": genre_matches,
        "score_ok": score_ok,
        "genre_ok": genre_ok,
        "num_reasons": len(top_reasons),
        "description": case["description"],
    }


def print_summary(results: list) -> None:
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    avg_confidence = round(sum(r["confidence"] for r in results) / total, 2)
    avg_quality = round(sum(r["quality_score"] for r in results) / total, 2)

    print("\n" + "=" * 72)
    print("  VIBEFINDER EVALUATION HARNESS")
    print("=" * 72)

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        bar = "✓" if r["passed"] else "✗"
        print(f"\n  [{bar}] {r['name']}  —  {status}")
        print(f"      {r['description']}")
        print(f"      Top result : {r['top_song']} (genre={r['top_genre']}, score={r['top_score']})")
        print(f"      Confidence : {r['confidence']}   Quality : {r['quality_score']}   Reasons : {r['num_reasons']}")
        if not r["score_ok"]:
            print(f"      FAIL reason: top_score below minimum threshold")
        if not r["genre_ok"]:
            print(f"      FAIL reason: expected genre not in top-3 results")

    print("\n" + "-" * 72)
    print(f"  Results      : {passed}/{total} tests passed")
    print(f"  Avg confidence : {avg_confidence}   Avg quality score : {avg_quality}")
    print("=" * 72 + "\n")


def main():
    print("\nLoading catalog and running evaluation harness...")
    results = [run_test(case, SONGS) for case in TEST_CASES]
    print_summary(results)

    failed = [r for r in results if not r["passed"]]
    if failed:
        print(f"Failed tests: {[r['name'] for r in failed]}")
        sys.exit(1)
    else:
        print("All tests passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
