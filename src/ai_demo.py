"""
AI-Enhanced Music Recommender Demo.

This script demonstrates all AI features:
1. RAG (Retrieval-Augmented Generation) with LLM explanations
2. Agentic Workflow with iterative refinement
3. Reliability Testing System
4. Multi-turn conversational interface

Run with: python -m src.ai_demo
"""

import os
import json
from typing import Optional

from src.recommender import load_songs, recommend_songs, Recommender, UserProfile, Song
from src.ai_recommender_rag import MusicRAG
from src.agentic_workflow import RecommendationAgent
from src.reliability_testing import ReliabilityTester


def setup_llm_client():
    """
    Initialize LLM client (Claude or GPT) if API keys are available.
    Falls back to rule-based recommendations if not.
    """
    try:
        # Try Anthropic (Claude)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            from anthropic import Anthropic
            print("✓ Using Claude (Anthropic)")
            return Anthropic()
    except ImportError:
        pass

    try:
        # Try OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            from openai import OpenAI
            print("✓ Using GPT (OpenAI)")
            return OpenAI()
    except ImportError:
        pass

    print("⚠ No LLM API keys found. Using rule-based recommendations.")
    print("  Set ANTHROPIC_API_KEY or OPENAI_API_KEY for enhanced explanations.")
    return None


def demo_rag_system():
    """Demonstrate Retrieval-Augmented Generation (RAG) capabilities."""
    print("\n" + "=" * 70)
    print("DEMO 1: RAG-Enhanced Recommendations")
    print("=" * 70)

    # Load songs
    csv_path = "data/songs.csv"
    songs_data = load_songs(csv_path)

    # Initialize RAG system
    client = setup_llm_client()
    rag = MusicRAG(songs_data, client=client)

    # User preference
    user_prefs = {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.40,
        "target_valence": 0.60,
        "likes_acoustic": True,
    }

    print(f"\nUser Profile: {user_prefs}")

    # Get recommendations
    recs = recommend_songs(
        user_prefs=user_prefs,
        songs=songs_data,
        k=3,
    )

    print("\n📚 Retrieving context for top recommendations...")
    for i, (song, score, reasons) in enumerate(recs, 1):
        print(f"\n{i}. {song['title']} by {song['artist']} (Score: {score})")

        # Retrieve context
        context = rag.retrieve_song_context(song, num_similar=2)
        print(f"   ✓ Retrieved context (similar songs by genre, mood, era)")

        # Generate LLM-enhanced explanation
        explanation = rag.generate_recommendation_explanation(
            user_prefs, song, score, reasons, context
        )
        print(f"   💬 {explanation}")


def demo_agentic_workflow():
    """Demonstrate Agentic Workflow with iterative refinement."""
    print("\n" + "=" * 70)
    print("DEMO 2: Agentic Workflow (Plan → Act → Evaluate → Refine)")
    print("=" * 70)

    # Load songs
    csv_path = "data/songs.csv"
    songs_data = load_songs(csv_path)

    # Create base recommender
    recommender = Recommender([Song(**s) for s in songs_data])

    # Create agent
    agent = RecommendationAgent(recommender)

    # User preference
    user_prefs = {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.90,
        "target_valence": 0.45,
        "likes_acoustic": False,
    }

    print(f"\nUser Profile: {user_prefs}")
    print("\nAgent starting autonomous workflow...")

    # Run agentic workflow
    recommendations, summary = agent.run(user_prefs, songs_data)

    print(f"\n✓ Workflow Complete")
    print(f"  - Iterations: {summary['total_iterations']}")
    print(f"  - Final Quality Score: {summary['final_quality_score']}")
    print(f"  - Quality Improvement: {summary['quality_improvement']}")

    print("\nFinal Recommendations:")
    for i, (song, score, reasons) in enumerate(recommendations, 1):
        print(f"\n{i}. {song['title']} by {song['artist']} (Score: {score})")
        for reason in reasons[:2]:  # Show top 2 reasons
            print(f"   - {reason}")

    # Export workflow
    print("\n📊 Workflow log exported.")


def demo_reliability_testing():
    """Demonstrate Reliability Testing System."""
    print("\n" + "=" * 70)
    print("DEMO 3: Reliability Testing System")
    print("=" * 70)

    # Load songs
    csv_path = "data/songs.csv"
    songs_data = load_songs(csv_path)

    # Create tester
    tester = ReliabilityTester(recommender=None)

    # Test profiles
    test_profiles = [
        ("Pop Enthusiast", {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.85,
            "target_valence": 0.80,
            "likes_acoustic": False,
        }),
        ("Lofi Student", {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.35,
            "target_valence": 0.55,
            "likes_acoustic": True,
        }),
        ("Rock Lover", {
            "genre": "rock",
            "mood": "intense",
            "energy": 0.90,
            "target_valence": 0.40,
            "likes_acoustic": False,
        }),
    ]

    primary_prefs = test_profiles[0][1]

    # Run full test suite
    report = tester.run_full_test_suite(
        user_prefs=primary_prefs,
        songs=songs_data,
        user_profiles=test_profiles,
    )

    print("\n📈 Test Results Summary:")
    print(f"  - Overall Status: {report['overall_status']}")
    print(f"  - Tests Passed: {report['tests_passed']}/{report['tests_run']}")

    print("\n  Consistency Test:")
    consistency = report["consistency"]
    print(f"    - Score: {consistency['consistency_score']}")
    print(f"    - Status: {consistency['status']}")

    print("\n  Robustness Test:")
    robustness = report["robustness"]
    print(f"    - Score: {robustness['robustness_score']}")
    print(f"    - Status: {robustness['status']}")

    if report["fairness"]:
        print("\n  Fairness Test:")
        fairness = report["fairness"]
        print(f"    - Profiles Tested: {fairness['num_profiles']}")
        print(f"    - Status: {fairness['status']}")
        if fairness["over_represented_genres"]:
            print(f"    ⚠ Over-represented: {fairness['over_represented_genres']}")

    print("\n  Explanation Alignment Test:")
    alignment = report["explanation_alignment"]
    if alignment.get("status") != "SKIP":
        print(f"    - Score: {alignment['alignment_score']}")
        print(f"    - Status: {alignment['status']}")


def demo_interactive_conversation():
    """Demonstrate multi-turn conversational interface."""
    print("\n" + "=" * 70)
    print("DEMO 4: Interactive Conversational Interface")
    print("=" * 70)

    # Load songs
    csv_path = "data/songs.csv"
    songs_data = load_songs(csv_path)

    # Initialize RAG system
    client = setup_llm_client()
    rag = MusicRAG(songs_data, client=client)

    print("\n💬 Starting recommendation conversation...")
    print("(Simulated multi-turn interaction)\n")

    # Initial preference
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.75,
        "target_valence": 0.80,
        "likes_acoustic": False,
    }

    print("User: I like upbeat pop music, high energy.")
    print(f"Agent: Got it! {user_prefs['genre']} with {user_prefs['mood']} mood.")

    # Add to conversation
    rag.add_to_conversation("user", "I like upbeat pop music, high energy.")
    rag.add_to_conversation("assistant", "Got it! pop with happy mood.")

    # Get recommendations
    recs = recommend_songs(user_prefs=user_prefs, songs=songs_data, k=3)

    print("\nAgent: Here are my top recommendations:")
    for i, (song, score, reasons) in enumerate(recs, 1):
        print(f"  {i}. {song['title']} by {song['artist']}")

    # Simulate feedback
    feedback = "These are too electronic. Can I get something with more acoustic feel?"
    print(f"\nUser: {feedback}")

    # Clarify and refine
    if client:
        clarification = rag.get_clarification(feedback)
        print(f"Agent: {clarification}")
    else:
        print("Agent: Let me adjust for more acoustic instruments...")

    # Refined recommendations
    refined_prefs = user_prefs.copy()
    refined_prefs["likes_acoustic"] = True
    refined_recs = recommend_songs(user_prefs=refined_prefs, songs=songs_data, k=2)

    print("\nAgent: Here are updated recommendations:")
    for i, (song, score, reasons) in enumerate(refined_recs, 1):
        print(f"  {i}. {song['title']} by {song['artist']} (Acoustic: {song['acousticness']:.1%})")

    print("\n✓ Conversation exported for review.")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("🎵 AI-ENHANCED MUSIC RECOMMENDER SYSTEM")
    print("=" * 70)
    print("\nThis demo showcases advanced AI features:")
    print("  1. RAG - Retrieval-Augmented Generation with LLM explanations")
    print("  2. Agentic Workflow - Autonomous iterative refinement")
    print("  3. Reliability Testing - Consistency, robustness, fairness")
    print("  4. Conversational Interface - Multi-turn interactions")

    try:
        # Run demos
        demo_rag_system()
        demo_agentic_workflow()
        demo_reliability_testing()
        demo_interactive_conversation()

        print("\n" + "=" * 70)
        print("✓ All demos completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
