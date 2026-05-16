---
title: VibeFinder
emoji: 🎵
colorFrom: purple
colorTo: pink
sdk: streamlit
sdk_version: 1.36.0
app_file: app.py
pinned: false
---

# VibeFinder — AI-Enhanced Music Recommender

## Original Project

**Original project:** `ai110-musicW3` — Music Recommender Simulation (Modules 1–3)

The original project was a content-based music recommender built in Python from scratch. It represented 20 songs as structured data (genre, mood, energy, valence, acousticness) and scored them against a user taste profile using a weighted formula — awarding points for genre/mood matches and using proximity math for numerical features. The goal was to simulate how real recommenders like Spotify turn user data and song data into ranked predictions, and to discover where that process can go wrong or be unfair.

---

## Title and Summary

**VibeFinder** is an AI-enhanced music recommendation system that combines a content-based scoring engine with three advanced AI features: Retrieval-Augmented Generation (RAG) for context-aware explanations, an Agentic Workflow that autonomously plans and self-corrects recommendations, and a Reliability Testing Framework that validates consistency, robustness, and fairness.

It matters because music recommendation is a real AI problem — Spotify, YouTube Music, and Apple Music all face the exact challenges demonstrated here: catalog bias, cold-start problems, exact-match brittleness, and fairness across underrepresented genres. Building this system from scratch, then layering AI on top, makes those challenges concrete and measurable.

---

## System Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────┐
│                     USER INPUT                              │
│         genre · mood · energy · valence · acoustic          │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────▼─────────────┐
          │      RAG RETRIEVER       │
          │  Looks up similar songs  │
          │  by genre, mood, era     │
          │  Builds context window   │
          └────────────┬─────────────┘
                       │  context
          ┌────────────▼─────────────┐
          │    SCORING ENGINE        │
          │  score_song() per song   │
          │  Modes: default /        │
          │  mood_first /            │
          │  energy_focused /        │
          │  popularity_aware        │
          └────────────┬─────────────┘
                       │  scored list
          ┌────────────▼─────────────┐
          │   RECOMMENDATION AGENT   │
          │  PLAN → ACT → EVALUATE   │
          │        → REFINE          │
          │  Quality threshold: 0.65 │
          │  Max iterations: 3       │
          └────────────┬─────────────┘
                       │  top-K songs + quality score
          ┌────────────▼─────────────┐
          │       LLM EXPLAINER      │
          │  Claude / GPT or         │
          │  rule-based fallback     │
          │  "Recommended because…"  │
          └────────────┬─────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                     OUTPUT                                  │
│    Top-5 songs · scores · explanations · quality metrics    │
└─────────────────────────────────────────────────────────────┘

        ┌────────────────────────────────────┐
        │      RELIABILITY TESTING           │  ← runs independently
        │  Consistency · Robustness          │
        │  Fairness · Explanation Alignment  │
        │  Human / automated review point    │
        └────────────────────────────────────┘
```

**Data flow:** User preferences enter the RAG Retriever, which pulls similar songs from the catalog to build context. The Scoring Engine evaluates every song. The Recommendation Agent runs a plan-act-evaluate-refine loop, adjusting strategy if quality falls below 0.65. The LLM Explainer adds natural-language reasoning. Reliability Testing runs separately on any profile to validate that outputs are consistent and fair.

**Human evaluation point:** The Reliability Testing module is where a human (or automated harness) reviews outputs. The fairness test flags over-represented genres (>40% of results from one genre) for human review.

---

## Architecture Overview (Component Details)

| Component | File | Role |
| --------- | ---- | ---- |
| Scoring Engine | `src/recommender.py` | Core algorithm — 4 scoring modes, diversity penalty |
| RAG Retriever | `src/ai_recommender_rag.py` | Retrieves context, calls LLM, multi-turn conversation |
| Recommendation Agent | `src/agentic_workflow.py` | Autonomous Plan→Act→Evaluate→Refine loop |
| Reliability Tester | `src/reliability_testing.py` | Consistency, robustness, fairness, alignment tests |
| Demo Runner | `src/ai_demo.py` | End-to-end walkthrough of all AI features |
| Eval Harness | `tests/eval_harness.py` | Predefined-input evaluation with pass/fail scoring |

---

## Setup Instructions

### Step 1 — Clone and create virtual environment

```bash
git clone <your-repo-url>
cd applied-ai-system-project
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
# .venv\Scripts\activate         # Windows
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — (Optional) Add LLM API key for natural-language explanations

Without a key the system still works — it falls back to rule-based explanations.

```bash
export ANTHROPIC_API_KEY=your_key_here   # for Claude
# OR
export OPENAI_API_KEY=your_key_here      # for GPT
```

### Step 4 — Run the original recommender

```bash
python -m src.main
```

### Step 5 — Run the AI-enhanced demo

```bash
python -m src.ai_demo
```

### Step 6 — Run all tests

```bash
pytest tests/ -v
```

### Step 7 — Run the evaluation harness (extra credit)

```bash
python tests/eval_harness.py
```

---

## Sample Interactions

### Interaction 1 — Basic Recommendation (Default Mode)

**Input:**

```python
user_prefs = {
    "genre": "lofi",
    "mood": "chill",
    "energy": 0.40,
    "likes_acoustic": True
}
```

**Output:**

```text
+-----+-------------------+-----------------+-------+-------+-------+-----------------------------------+
|   # | Title             | Artist          | Genre | Mood  | Score | Why                               |
+=====+===================+=================+=======+=======+=======+===================================+
|   1 | Library Rain      | Paper Lanterns  | lofi  | chill |  5.08 | genre match (+2.0), mood match    |
|   2 | Midnight Coding   | LoRoom          | lofi  | chill |  4.86 | genre match (+2.0), mood match    |
|   3 | Pillow Drift      | Coma Naps       | lofi  | chill |  4.75 | genre match (+2.0), mood match    |
|   4 | Focus Flow        | Beta Waves      | lofi  | focus |  3.86 | genre match (+2.0), energy close  |
|   5 | Coffee Shop       | Brewed Muse     | jazz  | chill |  2.40 | mood match (+1.0)                 |
+-----+-------------------+-----------------+-------+-------+-------+-----------------------------------+
```

**What happened:** Genre match fired for all three lofi songs, giving them a +2.0 head start. Among lofi songs, energy proximity and acousticness bonus distinguished the ranking. The jazz song slipped in at #5 because it matched mood but not genre — demonstrating the genre weight dominance.

---

### Interaction 2 — Agentic Workflow (Plan → Act → Evaluate → Refine)

**Input:**

```python
user_prefs = {
    "genre": "pop",
    "mood": "happy",
    "energy": 0.85,
    "target_valence": 0.80
}
```

**Agent Output:**

```text
[AGENT] Step 1 — PLAN
  Strategy: mode=default, diversity_penalty=False
  Constraints: min_genre_match=2, min_score=2.5

[AGENT] Step 2 — ACT
  Generated 5 recommendations using default mode

[AGENT] Step 3 — EVALUATE
  genre_match_rate: 0.40   (2/5 songs match genre)
  mood_match_rate:  0.40
  energy_alignment: 0.91
  diversity_score:  0.80
  avg_score:        3.52
  quality_score:    0.72   ← above threshold (0.65), DONE

[AGENT] Result: COMPLETE in 1 iteration
  Quality improved from 0.00 → 0.72
```

**What happened:** The agent planned a strategy, executed it, evaluated quality across 5 metrics, and finished in one iteration because quality (0.72) exceeded the 0.65 threshold. Had it fallen short, it would have switched scoring modes and retried.

---

### Interaction 3 — Reliability Test Suite

**Input:** Lofi/chill profile run through the full test suite.

**Output:**

```text
Running Reliability Test Suite...
  - Testing consistency...    PASS  (score: 1.00 — identical results across 5 runs)
  - Testing robustness...     PASS  (score: 1.00 — stable under ±10% energy variation)
  - Testing alignment...      PASS  (score: 1.00 — 6 specific reasons, all grounded)

Overall: PASS  |  3/3 tests passed

Top recommendation: Library Rain by Paper Lanterns (score: 5.08)
Explanation: genre match (+2.0): lofi, mood match (+1.0): chill,
             energy close to target (+0.95): 0.35,
             valence close to target (+0.50): 0.60,
             strong acoustic feel (+0.43): 0.86,
             mood tags match (+0.20): peaceful
```

**What happened:** The system ran the same profile five times and got identical results (deterministic algorithm). It then varied energy ±10% and confirmed the same top songs appeared. Explanation alignment checked that every reason was specific and grounded in actual song data.

---

## Design Decisions

### Why content-based filtering (not collaborative)?

Collaborative filtering requires user listening history. This project has none — just song metadata and a profile. Content-based filtering is transparent (you can read exactly why each song scored high), debuggable, and fair in a small-catalog setting. **Trade-off:** it cannot discover cross-genre taste the way Spotify's "people who liked X also liked Y" approach can.

### Why RAG instead of pure LLM?

A standalone LLM would hallucinate song titles and invent reasons. RAG grounds the LLM in actual catalog data — the retriever pulls the real songs, and the LLM only explains them. **Trade-off:** adds complexity (retriever + LLM call) and requires an API key for full functionality. Rule-based fallback covers the no-key case.

### Why an agentic Plan→Act→Evaluate→Refine loop?

Single-pass recommendations cannot self-correct. If the first scoring mode produces poor genre coverage, there is no way to recover without the evaluate-refine cycle. The agent catches low-quality outputs (below 0.65 threshold) and switches modes automatically. **Trade-off:** up to 3 LLM-free iterations add latency (~100ms each); most profiles converge in 1.

### Why four scoring modes?

Different users weight features differently. A user who only cares about energy is poorly served by genre-first scoring. Having `default`, `mood_first`, `energy_focused`, and `popularity_aware` modes lets the agent pick the strategy that fits the profile. **Trade-off:** more modes = more complexity in the agent's planning logic.

### Why a diversity penalty?

Without it, the top 5 results could all be from the same artist (if that artist has multiple high-scoring songs). Diversity matters for recommendation quality. **Trade-off:** the penalty (−15%) can occasionally suppress a genuinely excellent second song from the same artist.

---

## Testing Summary

**Test results:** 19/19 tests passed (100%).

```text
tests/test_ai_features.py::TestMusicRAG               — 5/5  PASS
tests/test_ai_features.py::TestRecommendationAgent    — 4/4  PASS
tests/test_ai_features.py::TestReliabilityTester      — 6/6  PASS
tests/test_ai_features.py::TestIntegration            — 2/2  PASS
tests/test_recommender.py                             — 2/2  PASS
```

**Reliability scores (lofi/chill profile):**

- Consistency: **1.00** — identical top-5 across all 5 runs (deterministic algorithm)
- Robustness: **1.00** — same top songs persist under ±10% energy variation
- Explanation alignment: **1.00** — every explanation contains multiple specific, grounded reasons

**What worked:** The scoring engine is highly consistent because it is deterministic — same inputs always produce same outputs. The rule-based fallback for RAG explanations works without any API key, covering the no-LLM case gracefully. The agentic workflow converged in 1 iteration for all tested profiles.

**What did not work:** The fairness test was skipped in automated runs (requires multiple user profiles to be meaningful). LLM-powered explanations require an Anthropic or OpenAI API key — without one, the RAG module falls back to rule-based text, which is less natural. The catalog (20 songs) is too small to fairly serve users whose genre is not represented (reggae, classical, gospel).

**What I learned:** Deterministic algorithms score perfectly on consistency but that is not the same as being *correct* — you can be consistently wrong. The adversarial profiles (reggae, high-energy blues) revealed that consistency and relevance are independent: the system consistently returned poor results for underserved genres. Testing needs both reliability metrics *and* relevance metrics.

---

## Reflection

**What this project taught me about AI:**

The biggest lesson: AI systems do not fail randomly — they fail *systematically* along the lines of their training data and design assumptions. Every failure mode in this system was predictable from the algorithm design: the genre weight dominance, the exact-match brittleness, the catalog bias. Building the scoring engine first and then testing it against adversarial profiles made those failure modes visible before adding LLM layers on top. That order — build simple, test hard, then add AI — was the right sequence.

The agentic workflow taught me that self-correction is not magic. The agent can only switch between four pre-programmed scoring modes. It cannot invent a new strategy. Real agentic AI systems have the same constraint at a larger scale — they can combine tools and retry, but they cannot reason outside the boundaries of what they were designed to do. Understanding that boundary is important before deploying any AI agent.

---

## Reflection and Ethics

### Limitations and Biases

- **Catalog bias:** 20 songs covering ~12 genres. Users whose preferred genre (reggae, classical, gospel, R&B) is absent get meaningless results — not because the algorithm is unfair, but because the data is missing.
- **Exact-match brittleness:** "indie pop" and "pop" score 0 on genre match despite overlapping heavily. String matching has no semantic understanding.
- **Genre weight dominance:** Genre worth 2× mood means an intense pop song always outranks a perfectly chill jazz song for a pop user — even if the user explicitly asked for chill. Weights are fixed, not user-adjustable.
- **No history:** The system recommends the same songs every run. It cannot learn from skips, replays, or feedback within a session.

### Could the AI be misused?

At this scale: no serious misuse risk — it is a classroom catalog of 20 songs. At production scale, the risks would be:

- **Filter bubbles:** A genre-heavy scoring system traps users in the same three artists and never surfaces new genres.
- **Popularity bias:** The `popularity_aware` mode could systematically deprioritize independent artists in favor of mainstream ones.
- **Fairness across demographics:** If the catalog is built by one demographic, underrepresented genres suffer. Prevention: audit catalog composition before deployment; add genre diversity requirements to the scoring engine.

### What surprised me while testing

The consistency score of 1.00 was initially reassuring, then alarming. It means the system is perfectly repeatable — but the adversarial reggae profile is *also* perfectly repeatable in returning useless results. Reliability testing alone cannot tell you if results are *good*, only if they are *stable*. That distinction was the most important insight from the testing phase.

### AI Collaboration During This Project

**Helpful instance:** When I was designing the scoring modes, AI suggested adding a `diversity_penalty` flag that reduces the score of songs from artists already in the top results. I had not considered this — I was only thinking about scoring one song at a time. The diversity penalty (−15% for repeat artists) meaningfully improved result variety without changing the core scoring logic.

**Flawed instance:** Early in the project, AI generated a test for `test_agent_evaluate` that used `Recommender([])` but did not include the `Recommender` import in that specific test method — only `recommend_songs` was imported. The test file ran 18/19 tests before the missing import caused a `NameError`. The AI had scaffolded the test correctly in terms of logic but missed the dependency. I had to read the traceback and manually add `from src.recommender import recommend_songs, Recommender` to fix it. Lesson: always run tests immediately after AI generates them — do not assume imports are complete.

---

## Running the Original Recommender

```bash
python -m src.main        # all 4 scoring mode challenges
pytest tests/ -v          # 19/19 tests
```

See [model_card.md](model_card.md) for algorithm analysis, bias documentation, and evaluation against 5 user profiles.

---

## Original Algorithm Reference

| Signal | Max Points | Rule |
| ------ | ---------- | ---- |
| Genre match | +2.0 | Binary |
| Mood match | +1.0 | Binary |
| Energy closeness | 0.0–1.0 | Proximity `1 - abs(diff)` |
| Valence closeness | 0.0–0.5 | Proximity |
| Acoustic preference | 0.0–0.5 | Proximity |

Genre is 2× mood because genre is a hard filter — a jazz fan frustrated by a relaxed pop song confirms this: genre mismatch overrides mood alignment for most listeners.
