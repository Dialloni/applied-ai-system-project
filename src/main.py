"""
Command-line runner for the Music Recommender Simulation with 4 Advanced Challenges.

Run from the project root:
    python -m src.main

Challenges implemented:
1. Advanced Song Features: popularity, release_decade, detailed_mood_tags
2. Multiple Scoring Modes: genre-first, mood-first, energy-focused, popularity-aware
3. Diversity Penalty: prevents same artist from appearing multiple times
4. Visual Summary Table: tabulate-based formatted output (Challenge 4)
"""

from src.recommender import load_songs, recommend_songs

# Try to import tabulate for Challenge 4 (visual tables)
try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False
    print("Note: Install 'tabulate' for prettier table output: pip install tabulate")

# ── User profiles ──────────────────────────────────────────────────────────────

PROFILES = {
    "High-Energy Pop Fan": {
        "genre":          "pop",
        "mood":           "happy",
        "energy":         0.90,
        "target_valence": 0.85,
        "likes_acoustic": False,
    },

    "Chill Lofi Student": {
        "genre":          "lofi",
        "mood":           "chill",
        "energy":         0.38,
        "target_valence": 0.58,
        "likes_acoustic": True,
    },

    "Deep Intense Rock": {
        "genre":          "rock",
        "mood":           "intense",
        "energy":         0.92,
        "target_valence": 0.45,
        "likes_acoustic": False,
    },

    "Adversarial: High-Energy Blues (Conflicting)": {
        "genre":          "blues",
        "mood":           "sad",
        "energy":         0.90,
        "target_valence": 0.20,
        "likes_acoustic": True,
    },

    "Edge Case: Genre Not in Catalog (Reggae)": {
        "genre":          "reggae",
        "mood":           "relaxed",
        "energy":         0.60,
        "target_valence": 0.75,
        "likes_acoustic": False,
    },
}

# Challenge 1: New profile that uses detailed mood tags (advanced feature)
MOOD_TAG_PROFILE = {
    "genre":           "lofi",
    "mood":            "chill",
    "energy":          0.40,
    "target_valence":  0.60,
    "likes_acoustic":  True,
    "mood_tags":       ["nostalgic", "dreamy", "peaceful"],  # Challenge 1: Uses new feature
}

EXPERIMENT_WEIGHTS = {
    "genre":    1.0,
    "mood":     1.0,
    "energy":   2.0,
    "valence":  0.5,
    "acoustic": 0.5,
}


def print_results(profile_name: str, user_prefs: dict, results: list, mode: str = "default") -> None:
    """Prints a formatted block of recommendations with optional Challenge 4 table."""
    print()
    print("=" * 70)
    print(f"  {profile_name} (Mode: {mode})")
    print("=" * 70)
    print(
        f"  genre={user_prefs.get('genre')}  |  "
        f"mood={user_prefs.get('mood')}  |  "
        f"energy={user_prefs.get('energy')}"
    )
    print("-" * 70)
    
    # Challenge 4: Visual Summary Table
    if TABULATE_AVAILABLE and results:
        table_data = []
        for rank, (song, score, reasons) in enumerate(results, start=1):
            table_data.append([
                rank,
                song['title'],
                song['artist'],
                song['genre'],
                song['mood'],
                f"{score:.2f}",
                "; ".join(reasons[:1]),  # First reason only for table
            ])
        
        headers = ["#", "Title", "Artist", "Genre", "Mood", "Score", "Why"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    else:
        # Fallback to original bullet format
        for rank, (song, score, reasons) in enumerate(results, start=1):
            print(f"\n  #{rank}  {song['title']}  —  {song['artist']}")
            print(f"       Score  : {score:.2f}")
            print(f"       Genre  : {song['genre']}   Mood : {song['mood']}   Energy : {song['energy']}")
            print("       Why    :")
            for reason in reasons:
                print(f"         • {reason}")
    print()


def main() -> None:
    """Demonstrates all 4 challenges."""
    songs = load_songs("data/songs.csv")

    # ──────────────────────────────────────────────────────────────────────────
    # CHALLENGE 1: Advanced Song Features
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "█" * 70)
    print("  CHALLENGE 1 — Advanced Song Features (Popularity, Decade, Mood Tags)")
    print("█" * 70)
    print("\n  Songs now have:")
    print("    • Popularity (0-100): " + ", ".join([f"{s['title']} ({s['popularity']})" for s in songs[:3]]))
    print("    • Release Decade: " + ", ".join([f"{s['title']} ({s['release_decade']})" for s in songs[:3]]))
    print("    • Detailed Mood Tags: " + f"{songs[0]['title']} {songs[0]['detailed_mood_tags']}")

    # ──────────────────────────────────────────────────────────────────────────
    # CHALLENGE 2: Multiple Scoring Modes
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "█" * 70)
    print("  CHALLENGE 2 — Multiple Scoring Modes")
    print("█" * 70)

    pop_prefs = PROFILES["High-Energy Pop Fan"]
    
    print("\n  Mode 1: DEFAULT (Genre-First)")
    default_results = recommend_songs(pop_prefs, songs, k=5, mode="default")
    print_results("DEFAULT MODE", pop_prefs, default_results, mode="default")
    
    print("  Mode 2: MOOD-FIRST (Mood is primary signal)")
    mood_first_results = recommend_songs(pop_prefs, songs, k=5, mode="mood_first")
    print_results("MOOD-FIRST MODE", pop_prefs, mood_first_results, mode="mood_first")
    
    print("  Mode 3: ENERGY-FOCUSED (Energy dominates)")
    energy_results = recommend_songs(pop_prefs, songs, k=5, mode="energy_focused")
    print_results("ENERGY-FOCUSED MODE", pop_prefs, energy_results, mode="energy_focused")

    # ──────────────────────────────────────────────────────────────────────────
    # CHALLENGE 3: Diversity Penalty
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "█" * 70)
    print("  CHALLENGE 3 — Diversity Penalty (Prevents Duplicate Artists)")
    print("█" * 70)

    print("\n  WITHOUT Diversity Penalty:")
    results_no_diversity = recommend_songs(pop_prefs, songs, k=5, diversity_penalty=False)
    for rank, (song, score, _) in enumerate(results_no_diversity, 1):
        print(f"    #{rank}  {song['title']} by {song['artist']} [{score:.2f}]")

    print("\n  WITH Diversity Penalty (penalizes duplicate artists):")
    results_with_diversity = recommend_songs(pop_prefs, songs, k=5, diversity_penalty=True)
    for rank, (song, score, _) in enumerate(results_with_diversity, 1):
        print(f"    #{rank}  {song['title']} by {song['artist']} [{score:.2f}]")

    # ──────────────────────────────────────────────────────────────────────────
    # CHALLENGE 4: Visual Summary Table (already shown above with tabulate)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "█" * 70)
    print("  CHALLENGE 4 — Visual Summary Tables (shown above with tabulate)")
    print("█" * 70)
    print("\n  Tables display rank, title, artist, genre, mood, score, and reasons.")
    if not TABULATE_AVAILABLE:
        print("  Install tabulate for better formatting: pip install tabulate")

    print()


if __name__ == "__main__":
    main()
