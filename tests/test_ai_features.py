"""
Tests for AI-Enhanced Music Recommender System.

Tests for:
- RAG system (retrieval and explanation generation)
- Agentic workflow (planning, acting, evaluating, refining)
- Reliability testing (consistency, robustness, fairness)
"""

import pytest
from src.recommender import load_songs
from src.ai_recommender_rag import MusicRAG
from src.agentic_workflow import RecommendationAgent, AgentState
from src.reliability_testing import ReliabilityTester


@pytest.fixture
def sample_songs():
    """Load sample songs for testing."""
    return load_songs("data/songs.csv")


@pytest.fixture
def sample_user_prefs():
    """Sample user preferences."""
    return {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.40,
        "target_valence": 0.60,
        "likes_acoustic": True,
    }


class TestMusicRAG:
    """Test cases for RAG system."""

    def test_rag_initialization(self, sample_songs):
        """Test RAG system initialization."""
        rag = MusicRAG(sample_songs, client=None)
        assert rag is not None
        assert len(rag.songs) > 0
        assert rag.client is None

    def test_retrieve_song_context(self, sample_songs):
        """Test song context retrieval."""
        rag = MusicRAG(sample_songs)
        song = sample_songs[0]
        
        context = rag.retrieve_song_context(song, num_similar=2)
        
        assert "song" in context
        assert context["song"] == song
        assert "similar_by_genre" in context
        assert "similar_by_mood" in context
        assert "similar_by_era" in context

    def test_retrieve_user_context(self, sample_songs, sample_user_prefs):
        """Test user context retrieval."""
        rag = MusicRAG(sample_songs)
        
        context = rag.retrieve_user_context(sample_user_prefs)
        
        assert "user_preferences" in context
        assert "exact_matches" in context
        assert "close_matches" in context

    def test_conversation_history(self, sample_songs, sample_user_prefs):
        """Test conversation history tracking."""
        rag = MusicRAG(sample_songs)
        
        rag.add_to_conversation("user", "I like lofi music")
        rag.add_to_conversation("assistant", "Great! I can recommend lofi tracks")
        
        assert len(rag.conversation_history) == 2
        assert rag.conversation_history[0]["role"] == "user"
        assert rag.conversation_history[1]["role"] == "assistant"

    def test_fallback_explanation(self, sample_songs, sample_user_prefs):
        """Test fallback explanation when LLM is unavailable."""
        rag = MusicRAG(sample_songs, client=None)
        song = sample_songs[0]
        reasons = ["genre matches", "energy is close"]
        
        explanation = rag._fallback_explanation(sample_user_prefs, song, reasons)
        
        assert isinstance(explanation, str)
        assert song["title"] in explanation
        assert len(explanation) > 0


class TestRecommendationAgent:
    """Test cases for agentic workflow."""

    def test_agent_initialization(self):
        """Test agent initialization."""
        from src.recommender import Recommender
        
        recommender = Recommender([])
        agent = RecommendationAgent(recommender)
        
        assert agent is not None
        assert agent.state == AgentState.ANALYZING
        assert agent.iteration_count == 0

    def test_agent_plan(self, sample_songs, sample_user_prefs):
        """Test planning phase."""
        from src.recommender import Recommender
        
        recommender = Recommender([])
        agent = RecommendationAgent(recommender)
        
        strategy = agent.plan(sample_user_prefs)
        
        assert "step" in strategy
        assert strategy["step"] == "plan"
        assert "constraints" in strategy
        assert "scoring_mode" in strategy

    def test_agent_evaluate(self, sample_songs, sample_user_prefs):
        """Test evaluation phase."""
        from src.recommender import recommend_songs, Recommender

        recommender = Recommender([])
        agent = RecommendationAgent(recommender)
        
        recs = recommend_songs(sample_user_prefs, sample_songs, k=3)
        quality_score, evaluation = agent.evaluate(recs, sample_user_prefs)
        
        assert isinstance(quality_score, float)
        assert 0 <= quality_score <= 1
        assert "metrics" in evaluation
        assert "genre_match_rate" in evaluation["metrics"]

    def test_agent_workflow(self, sample_songs, sample_user_prefs):
        """Test complete agent workflow."""
        from src.recommender import Recommender
        
        recommender = Recommender([])
        agent = RecommendationAgent(recommender)
        
        recommendations, summary = agent.run(sample_user_prefs, sample_songs)
        
        assert isinstance(summary, dict)
        assert "total_iterations" in summary
        assert "final_quality_score" in summary
        assert agent.state == AgentState.COMPLETE


class TestReliabilityTester:
    """Test cases for reliability testing system."""

    def test_tester_initialization(self):
        """Test tester initialization."""
        tester = ReliabilityTester(recommender=None)
        assert tester is not None
        assert len(tester.test_results) == 0

    def test_consistency_test(self, sample_songs, sample_user_prefs):
        """Test consistency testing."""
        tester = ReliabilityTester(recommender=None)
        
        result = tester.test_consistency(sample_user_prefs, sample_songs, num_runs=3)
        
        assert result["test_name"] == "consistency"
        assert "consistency_score" in result
        assert 0 <= result["consistency_score"] <= 1
        assert result["status"] in ["PASS", "FAIL"]

    def test_robustness_test(self, sample_songs, sample_user_prefs):
        """Test robustness testing."""
        tester = ReliabilityTester(recommender=None)
        
        result = tester.test_robustness(sample_user_prefs, sample_songs)
        
        assert result["test_name"] == "robustness"
        assert "robustness_score" in result
        assert 0 <= result["robustness_score"] <= 1

    def test_fairness_test(self, sample_songs):
        """Test fairness testing."""
        tester = ReliabilityTester(recommender=None)
        
        profiles = [
            ("Profile 1", {"genre": "lofi", "mood": "chill", "energy": 0.4, "likes_acoustic": True}),
            ("Profile 2", {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}),
        ]
        
        result = tester.test_fairness(profiles, sample_songs)
        
        assert result["test_name"] == "fairness"
        assert "genre_distribution" in result
        assert "artist_distribution" in result
        assert result["status"] in ["PASS", "WARN"]

    def test_explanation_alignment(self, sample_songs, sample_user_prefs):
        """Test explanation alignment testing."""
        tester = ReliabilityTester(recommender=None)
        
        song = sample_songs[0]
        score = 3.5
        reasons = ["genre matches", "energy is close"]
        
        result = tester.test_explanation_alignment(
            sample_user_prefs, song, score, reasons
        )
        
        assert result["test_name"] == "explanation_alignment"
        assert "alignment_score" in result
        assert result["status"] in ["PASS", "FAIL"]

    def test_full_test_suite(self, sample_songs, sample_user_prefs):
        """Test full test suite."""
        tester = ReliabilityTester(recommender=None)
        
        profiles = [
            ("Profile 1", sample_user_prefs),
            ("Profile 2", {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}),
        ]
        
        report = tester.run_full_test_suite(sample_user_prefs, sample_songs, user_profiles=profiles)
        
        assert "overall_status" in report
        assert "tests_run" in report
        assert "tests_passed" in report
        assert report["overall_status"] in ["PASS", "WARN", "FAIL"]


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_rag_with_recommendations(self, sample_songs, sample_user_prefs):
        """Test RAG system with recommendations."""
        from src.recommender import recommend_songs
        
        rag = MusicRAG(sample_songs)
        recs = recommend_songs(sample_user_prefs, sample_songs, k=2)
        
        for song, score, reasons in recs:
            context = rag.retrieve_song_context(song)
            explanation = rag.generate_recommendation_explanation(
                sample_user_prefs, song, score, reasons, context
            )
            
            assert isinstance(explanation, str)
            assert len(explanation) > 0

    def test_agent_with_tester(self, sample_songs, sample_user_prefs):
        """Test agent workflow with reliability testing."""
        from src.recommender import Recommender
        
        recommender = Recommender([])
        agent = RecommendationAgent(recommender)
        tester = ReliabilityTester(recommender)
        
        # Run agent
        recommendations, summary = agent.run(sample_user_prefs, sample_songs)
        
        # Test reliability
        if recommendations:
            test_result = tester.test_consistency(sample_user_prefs, sample_songs, num_runs=2)
            assert test_result["status"] in ["PASS", "FAIL"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
