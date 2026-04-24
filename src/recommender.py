from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv


# Default scoring weights — change these to run experiments
DEFAULT_WEIGHTS: Dict[str, float] = {
    "genre":    2.0,   # binary match bonus
    "mood":     1.0,   # binary match bonus
    "energy":   1.0,   # multiplier on proximity score (0-1 range)
    "valence":  0.5,   # max possible valence proximity points
    "acoustic": 0.5,   # max possible acoustic preference points
}

# Scoring mode weights for Challenge 2: Multiple Scoring Modes
MOOD_FIRST_WEIGHTS: Dict[str, float] = {
    "genre":    1.0,   # reduced — mood is now primary
    "mood":     2.0,   # doubled — mood is king
    "energy":   0.8,
    "valence":  0.5,
    "acoustic": 0.3,
}

ENERGY_FOCUSED_WEIGHTS: Dict[str, float] = {
    "genre":    1.5,
    "mood":     0.5,
    "energy":   2.0,   # doubled — energy dominates
    "valence":  1.0,
    "acoustic": 0.5,
}

POPULARITY_AWARE_WEIGHTS: Dict[str, float] = {
    "genre":    1.8,
    "mood":     0.9,
    "energy":   0.9,
    "valence":  0.5,
    "acoustic": 0.5,
    "popularity": 1.0,  # new feature
    "decade": 0.3,      # new feature
}


@dataclass
class Song:
    """Represents a song and its audio attributes loaded from the CSV catalog."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_decade: str = "2020s"
    detailed_mood_tags: list = None

    def __post_init__(self):
        if self.detailed_mood_tags is None:
            self.detailed_mood_tags = []


@dataclass
class UserProfile:
    """Represents a listener's taste preferences used by the OOP Recommender."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """OOP recommender that scores and ranks Song objects against a UserProfile."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> float:
        """
        Returns a numeric match score for one song against a user profile.

        Scoring breakdown (max ~4.5):
          +2.0  genre match      (binary — strongest signal)
          +1.0  mood match       (binary — secondary signal)
          +1.0  energy closeness (1.0 - abs difference)
          +0.5  acoustic preference bonus
        """
        score = 0.0

        if song.genre == user.favorite_genre:
            score += 2.0

        if song.mood == user.favorite_mood:
            score += 1.0

        energy_diff = abs(song.energy - user.target_energy)
        score += 1.0 - energy_diff

        if user.likes_acoustic:
            score += song.acousticness * 0.5
        else:
            score += (1.0 - song.acousticness) * 0.5

        return score

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top-k songs ranked highest to lowest by match score."""
        return sorted(self.songs, key=lambda s: self._score(user, s), reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable string explaining why a song was recommended."""
        reasons = []

        if song.genre == user.favorite_genre:
            reasons.append(f"genre matches your favorite ({song.genre})")

        if song.mood == user.favorite_mood:
            reasons.append(f"mood matches your preference ({song.mood})")

        energy_diff = abs(song.energy - user.target_energy)
        if energy_diff < 0.15:
            reasons.append(f"energy level is close to your target ({song.energy:.2f})")

        if user.likes_acoustic and song.acousticness > 0.6:
            reasons.append(f"it has a strong acoustic feel ({song.acousticness:.2f})")
        elif not user.likes_acoustic and song.acousticness < 0.3:
            reasons.append(f"it has a non-acoustic sound you prefer ({song.acousticness:.2f})")

        if not reasons:
            reasons.append("it's a reasonable overall fit for your taste")

        return "Recommended because: " + ", ".join(reasons) + "."


# ──────────────────────────────────────────────────────────────────────────────
# Functional API — used by src/main.py
# ──────────────────────────────────────────────────────────────────────────────

def load_songs(csv_path: str) -> List[Dict]:
    """Reads songs.csv and returns a list of dicts with numeric fields cast to float/int."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
                # Challenge 1: New advanced features
                "popularity":   int(row.get("popularity", 50)),  # 0-100 scale
                "release_decade": row.get("release_decade", "2020s"),  # e.g., "2020s", "2010s"
                "detailed_mood_tags": row.get("detailed_mood_tags", "").split(";"),  # semicolon-separated list
            })
    print(f"Loaded {len(songs)} songs with advanced features.")
    return songs


def score_song(
    user_prefs: Dict,
    song: Dict,
    weights: Optional[Dict] = None,
    mode: str = "default",
) -> Tuple[float, List[str]]:
    """
    Scores one song against user preferences with optional scoring mode.
    
    Modes:
    - "default": Original genre-first approach
    - "mood_first": Mood is the primary signal (Challenge 2)
    - "energy_focused": Energy dominates the score (Challenge 2)
    - "popularity_aware": Incorporates song popularity and release decade (Challenge 1)
    
    Returns (score, reasons) tuple.
    """
    # Select weights based on mode
    if mode == "mood_first":
        w = {**MOOD_FIRST_WEIGHTS, **(weights or {})}
    elif mode == "energy_focused":
        w = {**ENERGY_FOCUSED_WEIGHTS, **(weights or {})}
    elif mode == "popularity_aware":
        w = {**POPULARITY_AWARE_WEIGHTS, **(weights or {})}
    else:
        w = {**DEFAULT_WEIGHTS, **(weights or {})}
    
    score = 0.0
    reasons: List[str] = []

    # ── Genre (binary) ────────────────────────────────────────────────────────
    if song["genre"] == user_prefs.get("genre"):
        score += w["genre"]
        reasons.append(f"genre match (+{w['genre']}): {song['genre']}")

    # ── Mood (binary) ─────────────────────────────────────────────────────────
    if song["mood"] == user_prefs.get("mood"):
        score += w["mood"]
        reasons.append(f"mood match (+{w['mood']}): {song['mood']}")

    # ── Energy proximity ──────────────────────────────────────────────────────
    target_energy = user_prefs.get("energy", 0.5)
    energy_diff = abs(song["energy"] - target_energy)
    energy_points = round(w["energy"] * (1.0 - energy_diff), 2)
    score += energy_points
    if energy_diff < 0.15:
        reasons.append(f"energy close to target (+{energy_points}): {song['energy']:.2f}")

    # ── Valence proximity ─────────────────────────────────────────────────────
    target_valence = user_prefs.get("target_valence")
    if target_valence is not None:
        valence_diff = abs(song["valence"] - target_valence)
        valence_points = round(w["valence"] * (1.0 - valence_diff), 2)
        score += valence_points
        if valence_diff < 0.15:
            reasons.append(f"valence close to target (+{valence_points}): {song['valence']:.2f}")

    # ── Acoustic preference ───────────────────────────────────────────────────
    likes_acoustic = user_prefs.get("likes_acoustic", False)
    if likes_acoustic:
        acoustic_points = round(song["acousticness"] * w["acoustic"], 2)
        score += acoustic_points
        if song["acousticness"] > 0.6:
            reasons.append(f"strong acoustic feel (+{acoustic_points}): {song['acousticness']:.2f}")
    else:
        score += (1.0 - song["acousticness"]) * w["acoustic"]

    # ── Challenge 1: Popularity scoring (new feature)
    if "popularity" in w and mode == "popularity_aware":
        pop_score = round(song.get("popularity", 50) / 100.0 * w.get("popularity", 0), 2)
        if pop_score > 0.5:
            score += pop_score
            reasons.append(f"high popularity (+{pop_score})")

    # ── Challenge 1: Detailed mood tags (new feature)
    user_mood_tags = user_prefs.get("mood_tags", [])
    if user_mood_tags and song.get("detailed_mood_tags"):
        song_tags = [tag.strip() for tag in song["detailed_mood_tags"]]
        matching_tags = [tag for tag in user_mood_tags if tag in song_tags]
        if matching_tags:
            tag_bonus = round(len(matching_tags) * 0.2, 2)
            score += tag_bonus
            reasons.append(f"mood tags match (+{tag_bonus}): {','.join(matching_tags)}")

    if not reasons:
        reasons.append("general fit — no single feature matched strongly")

    return round(score, 2), reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    weights: Optional[Dict] = None,
    mode: str = "default",
    diversity_penalty: bool = False,
) -> List[Tuple[Dict, float, List[str]]]:
    """
    Scores every song in the catalog and returns the top-k sorted highest to lowest.

    Args:
        user_prefs: User preference dictionary
        songs: List of song dictionaries
        k: Number of recommendations to return
        weights: Optional custom weights
        mode: Scoring mode ("default", "mood_first", "energy_focused", "popularity_aware")
        diversity_penalty: If True, penalizes songs from artists already in top results (Challenge 3)

    Returns:
        List of (song_dict, score, reasons) tuples, sorted by score.
    
    Challenge 3: Diversity Penalty
        If an artist appears in the results, subsequent songs from the same artist
        get a score penalty to encourage variety.
    """
    # Score all songs
    scored = [
        (song, *score_song(user_prefs, song, weights=weights, mode=mode))
        for song in songs
    ]
    
    # Sort by score
    scored = sorted(scored, key=lambda x: x[1], reverse=True)
    
    # Challenge 3: Apply diversity penalty if enabled
    if diversity_penalty:
        seen_artists = set()
        penalized_scored = []
        
        for song, score, reasons in scored:
            artist = song.get("artist", "Unknown")
            
            if artist in seen_artists:
                # Penalize this song (reduce score by 15%)
                penalty = score * 0.15
                new_score = round(score - penalty, 2)
                reasons.append(f"(diversity penalty: -{penalty:.2f} — artist already featured)")
                penalized_scored.append((song, new_score, reasons))
            else:
                seen_artists.add(artist)
                penalized_scored.append((song, score, reasons))
        
        scored = sorted(penalized_scored, key=lambda x: x[1], reverse=True)
    
    return scored[:k]
