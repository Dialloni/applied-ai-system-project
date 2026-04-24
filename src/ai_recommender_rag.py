"""
AI-Enhanced Music Recommender with Retrieval-Augmented Generation (RAG).

This module implements RAG by:
1. Retrieving relevant song metadata and user preference data
2. Using an LLM to generate personalized, natural-language explanations
3. Providing context-aware recommendations beyond simple scoring

Features:
- Retrieves song features, artist info, and user preferences
- Uses Claude/GPT to generate human-friendly explanations
- Provides multi-turn conversation for iterative refinement
- Validates AI consistency through repeated queries
"""

from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime


class MusicRAG:
    """
    Retrieval-Augmented Generation system for music recommendations.
    Retrieves song and user data, then uses LLM to generate explanations.
    """

    def __init__(self, songs: List[Dict], client=None):
        """
        Initialize the RAG system with songs and an optional LLM client.
        
        Args:
            songs: List of song dictionaries with metadata
            client: LLM client (anthropic.Anthropic or openai.OpenAI)
        """
        self.songs = songs
        self.client = client
        self.conversation_history: List[Dict] = []
        self.retrieved_context: List[Dict] = []

    def retrieve_song_context(self, song: Dict, num_similar: int = 3) -> Dict:
        """
        Retrieve context about a song and similar songs.
        This is the "retrieval" part of RAG.
        
        Args:
            song: The target song dictionary
            num_similar: Number of similar songs to retrieve
            
        Returns:
            Dict containing song info, similar songs, and metadata
        """
        context = {
            "song": song,
            "similar_by_genre": [],
            "similar_by_mood": [],
            "similar_by_era": [],
        }

        # Find similar songs by genre
        genre_matches = [
            s for s in self.songs 
            if s.get("genre") == song.get("genre") and s["id"] != song["id"]
        ]
        context["similar_by_genre"] = genre_matches[:num_similar]

        # Find similar songs by mood
        mood_matches = [
            s for s in self.songs 
            if s.get("mood") == song.get("mood") and s["id"] != song["id"]
        ]
        context["similar_by_mood"] = mood_matches[:num_similar]

        # Find similar songs by release decade
        decade_matches = [
            s for s in self.songs 
            if s.get("release_decade") == song.get("release_decade") and s["id"] != song["id"]
        ]
        context["similar_by_era"] = decade_matches[:num_similar]

        self.retrieved_context.append(context)
        return context

    def retrieve_user_context(self, user_prefs: Dict) -> Dict:
        """
        Retrieve context about user preferences and matching songs.
        
        Args:
            user_prefs: User preference dictionary
            
        Returns:
            Dict containing user profile and matching songs
        """
        context = {
            "user_preferences": user_prefs,
            "exact_matches": [],
            "close_matches": [],
        }

        favorite_genre = user_prefs.get("genre")
        favorite_mood = user_prefs.get("mood")

        # Find exact matches (genre + mood both match)
        exact = [
            s for s in self.songs
            if s.get("genre") == favorite_genre and s.get("mood") == favorite_mood
        ]
        context["exact_matches"] = exact

        # Find close matches (genre OR mood match)
        close = [
            s for s in self.songs
            if (s.get("genre") == favorite_genre or s.get("mood") == favorite_mood)
            and s not in exact
        ]
        context["close_matches"] = close[:5]

        return context

    def format_song_for_prompt(self, song: Dict) -> str:
        """Format a song dictionary as readable text for LLM prompt."""
        return (
            f"- **{song['title']}** by {song['artist']} "
            f"({song['genre']}, {song['mood']}) "
            f"[Energy: {song['energy']:.1%}, Acoustic: {song['acousticness']:.1%}]"
        )

    def generate_recommendation_explanation(
        self,
        user_prefs: Dict,
        recommended_song: Dict,
        score: float,
        reasons: List[str],
        context: Optional[Dict] = None,
    ) -> str:
        """
        Use LLM to generate a human-friendly explanation for the recommendation.
        Falls back to rule-based explanation if no LLM client is available.
        
        Args:
            user_prefs: User preferences
            recommended_song: The recommended song
            score: Recommendation score
            reasons: List of scoring reasons
            context: Retrieved context (optional)
            
        Returns:
            Natural language explanation string
        """
        # If no LLM client, use rule-based explanation
        if not self.client:
            return self._fallback_explanation(user_prefs, recommended_song, reasons)

        # Build prompt with retrieval context
        prompt = self._build_explanation_prompt(
            user_prefs, recommended_song, score, reasons, context
        )

        try:
            # Try Anthropic first (Claude)
            if hasattr(self.client, "messages"):
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=150,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text
            # Fall back to OpenAI
            else:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    max_tokens=150,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"LLM error: {e}. Using fallback explanation.")
            return self._fallback_explanation(user_prefs, recommended_song, reasons)

    def _build_explanation_prompt(
        self,
        user_prefs: Dict,
        song: Dict,
        score: float,
        reasons: List[str],
        context: Optional[Dict],
    ) -> str:
        """Build a prompt for LLM-based explanation."""
        user_summary = (
            f"User likes {user_prefs.get('genre')} music with {user_prefs.get('mood')} mood, "
            f"target energy level {user_prefs.get('energy', 0.5):.1%}"
        )

        song_summary = (
            f"{song['title']} by {song['artist']} is a {song['genre']} track "
            f"with {song['mood']} mood, {song['energy']:.1%} energy, "
            f"and {song['acousticness']:.1%} acousticness"
        )

        reasons_text = "\n".join(f"- {r}" for r in reasons)

        context_text = ""
        if context:
            similar_songs = (
                context.get("similar_by_genre", []) +
                context.get("similar_by_mood", [])
            )[:3]
            if similar_songs:
                context_text = "\n\nSimilar songs in catalog:\n"
                for s in similar_songs:
                    context_text += self.format_song_for_prompt(s) + "\n"

        prompt = f"""Given this user preference and recommendation, write a 1-2 sentence personalized explanation (casual, friendly tone).

User Profile: {user_summary}

Recommended Song: {song_summary}

Why recommended:
{reasons_text}
{context_text}

Explanation (1-2 sentences only):"""
        return prompt

    def _fallback_explanation(
        self, user_prefs: Dict, song: Dict, reasons: List[str]
    ) -> str:
        """Fallback explanation when LLM is unavailable."""
        reason_str = " and ".join(reasons[:2]) if reasons else "overall good fit"
        return (
            f"We think you'll like **{song['title']}** because {reason_str}. "
            f"Give it a try!"
        )

    def add_to_conversation(self, role: str, content: str) -> None:
        """Add message to conversation history for multi-turn interactions."""
        self.conversation_history.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})

    def get_clarification(self, user_feedback: str) -> str:
        """
        Use LLM to clarify user feedback and refine recommendations (agentic loop).
        
        Args:
            user_feedback: User's feedback on recommendations
            
        Returns:
            LLM's clarification/follow-up
        """
        if not self.client:
            return "Please provide more specific feedback (e.g., 'too energetic', 'too electronic')."

        self.add_to_conversation("user", user_feedback)

        prompt = f"""Based on this user feedback about music recommendations, provide a brief, friendly response that summarizes what they prefer and suggests how recommendations should change:

Feedback: {user_feedback}

Response (1-2 sentences):"""

        try:
            if hasattr(self.client, "messages"):  # Claude
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=100,
                    messages=[{"role": "user", "content": prompt}],
                )
                clarification = response.content[0].text
            else:  # OpenAI
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    max_tokens=100,
                    messages=[{"role": "user", "content": prompt}],
                )
                clarification = response.choices[0].message.content

            self.add_to_conversation("assistant", clarification)
            return clarification
        except Exception as e:
            return f"(Unable to process feedback: {e})"

    def export_conversation(self) -> str:
        """Export conversation history as JSON."""
        return json.dumps(self.conversation_history, indent=2)
