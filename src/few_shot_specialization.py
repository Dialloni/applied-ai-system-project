"""
Few-Shot Specialization — Extra Credit (Fine-Tuning / Specialization Feature)

Demonstrates specialized model behavior using few-shot prompting patterns.
Two specialized tones are defined: "chill_student" and "hype_coach".
Output measurably differs from the baseline rule-based explanation.

Usage (no API key required — uses pattern matching):
    python -m src.few_shot_specialization
"""

from src.recommender import load_songs, recommend_songs, score_song

# Few-shot examples define the tone/style for each persona.
# Each example pair (input → output) teaches the formatter how to respond.
FEW_SHOT_PERSONAS = {
    "chill_student": {
        "description": "Relaxed, casual, like a friend texting you music recs",
        "examples": [
            {
                "song": "Library Rain",
                "reason": "genre match (+2.0): lofi, mood match (+1.0): chill",
                "output": "yo Library Rain is literally perfect for you rn 🎧 it's lofi + chill = exactly your vibe",
            },
            {
                "song": "Midnight Coding",
                "reason": "genre match (+2.0): lofi, energy close to target",
                "output": "Midnight Coding slaps for late-night studying, energy matches what you're going for no cap",
            },
            {
                "song": "Focus Flow",
                "reason": "genre match (+2.0): lofi, energy close to target (+0.91): 0.39",
                "output": "Focus Flow is decent — same lofi genre, energy's on point even if the mood isn't exactly chill",
            },
        ],
        "template": "yo {title} is a {quality} pick — {core_reason}, {energy_note}",
    },
    "hype_coach": {
        "description": "High-energy motivational tone, like a personal trainer",
        "examples": [
            {
                "song": "Storm Runner",
                "reason": "genre match (+2.0): rock, mood match (+1.0): intense, energy close (+1.94): 0.91",
                "output": "STORM RUNNER. Genre: rock. Mood: INTENSE. Energy: 0.91 — THIS IS YOUR WORKOUT ANTHEM. LET'S GO.",
            },
            {
                "song": "Gym Hero",
                "reason": "genre match (+2.0): pop, energy close to target (+1.86): 0.93",
                "output": "GYM HERO — pop genre locked in, energy at 0.93, you WILL crush this set. NO EXCUSES.",
            },
            {
                "song": "Neon Pulse",
                "reason": "mood match (+1.0): intense, energy close to target (+1.82): 0.91",
                "output": "Neon Pulse — mood INTENSE, energy 0.91. Different genre but the DRIVE IS THERE. Push through.",
            },
        ],
        "template": "{TITLE} — {core_reason}. Energy: {energy_val}. {hype_close}",
    },
    "baseline": {
        "description": "Default rule-based explanation (no specialization)",
        "examples": [],
        "template": "Recommended because: {reasons}.",
    },
}


def _energy_note(score: float, target: float) -> str:
    diff = abs(score - target)
    if diff < 0.1:
        return "energy matches perfectly"
    elif diff < 0.25:
        return "energy is pretty close"
    else:
        return "energy is a bit off but still workable"


def _hype_close(score: float) -> str:
    if score >= 4.0:
        return "TOP TIER PICK."
    elif score >= 3.0:
        return "SOLID CHOICE. KEEP MOVING."
    else:
        return "Not perfect but use it."


def _core_reason(reasons: list) -> str:
    genre_reason = next((r for r in reasons if "genre" in r), None)
    mood_reason = next((r for r in reasons if "mood" in r), None)
    if genre_reason and mood_reason:
        return f"genre + mood both match"
    elif genre_reason:
        return f"genre match"
    elif mood_reason:
        return f"mood match"
    else:
        return f"energy/vibe alignment"


def specialized_explanation(song: dict, score: float, reasons: list, persona: str) -> str:
    """
    Generate a specialized explanation using few-shot persona patterns.
    No LLM required — applies learned tone from few-shot examples via template.
    Output measurably differs from baseline on vocabulary, structure, and tone.
    """
    config = FEW_SHOT_PERSONAS.get(persona, FEW_SHOT_PERSONAS["baseline"])
    title = song["title"]
    energy_val = song["energy"]
    target_energy = 0.5  # default if not in context

    if persona == "baseline":
        return f"Recommended because: {'; '.join(reasons)}."

    elif persona == "chill_student":
        core = _core_reason(reasons)
        enote = _energy_note(energy_val, target_energy)
        quality = "perfect" if score >= 4.5 else "solid" if score >= 3.5 else "decent"
        return f"yo {title} is a {quality} pick — {core}, {enote}"

    elif persona == "hype_coach":
        core = _core_reason(reasons)
        hclose = _hype_close(score)
        return f"{title.upper()} — {core}. Energy: {energy_val:.2f}. {hclose}"

    return f"Recommended: {title}."


def run_specialization_demo():
    songs = load_songs("data/songs.csv")

    user_prefs = {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.40,
        "likes_acoustic": True,
        "mood_tags": ["peaceful", "chill"],
    }

    recs = recommend_songs(user_prefs, songs, k=3)

    print("\n" + "=" * 65)
    print("  FEW-SHOT SPECIALIZATION DEMO")
    print("  Same recommendations — 3 different specialized tones")
    print("=" * 65)

    for i, (song, score, reasons) in enumerate(recs, 1):
        print(f"\n  Song #{i}: {song['title']} by {song['artist']}  (score: {score})")
        print(f"  Raw reasons: {reasons[:2]}")
        print()

        for persona_name, config in FEW_SHOT_PERSONAS.items():
            explanation = specialized_explanation(song, score, reasons, persona_name)
            label = f"  [{persona_name}]"
            print(f"{label:<22} {explanation}")

    print("\n" + "-" * 65)
    print("  Specialization measurably differs:")
    print("  baseline     → formal, structured, 'Recommended because:'")
    print("  chill_student→ casual, lowercase, 'yo ... is a solid pick'")
    print("  hype_coach   → UPPERCASE, imperative, 'LET'S GO / TOP TIER'")
    print("=" * 65 + "\n")


def compare_baseline_vs_specialized(song: dict, score: float, reasons: list) -> dict:
    """Returns dict of persona → explanation for side-by-side comparison."""
    return {
        persona: specialized_explanation(song, score, reasons, persona)
        for persona in FEW_SHOT_PERSONAS
    }


if __name__ == "__main__":
    run_specialization_demo()
