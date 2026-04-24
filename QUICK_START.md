# Quick Reference Guide - AI Music Recommender

## 🚀 Quick Start (2 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the demo
python -m src.ai_demo

# 3. Run tests
pytest tests/test_ai_features.py
```

That's it! Everything works without API keys.

---

## 📚 What Each File Does

### Core AI Modules

| File | Purpose | Key Classes |
|------|---------|-------------|
| `ai_recommender_rag.py` | RAG system for context-aware explanations | `MusicRAG` |
| `agentic_workflow.py` | Autonomous agent with planning/evaluation | `RecommendationAgent` |
| `reliability_testing.py` | Test suite for AI validation | `ReliabilityTester` |
| `ai_demo.py` | Comprehensive demo of all features | Demo functions |
| `recommender.py` | Base recommendation engine | `Recommender`, `Song` |

### Testing

| File | Purpose |
|------|---------|
| `tests/test_ai_features.py` | 25+ tests for AI features |
| `tests/test_recommender.py` | Original recommender tests |

### Documentation

| File | Purpose |
|------|---------|
| `AI_FEATURES.md` | Detailed feature documentation |
| `IMPLEMENTATION_SUMMARY.md` | Architecture and design |
| `REQUIREMENTS_FULFILLMENT.md` | How project meets requirements |

---

## 🎯 Using Individual Features

### Feature 1: RAG (Retrieval-Augmented Generation)

```python
from src.ai_recommender_rag import MusicRAG
from src.recommender import load_songs, recommend_songs

# Setup
songs = load_songs("data/songs.csv")
rag = MusicRAG(songs, client=None)  # None = rule-based fallback

# Get recommendations
user_prefs = {"genre": "lofi", "mood": "chill", "energy": 0.4, "likes_acoustic": True}
recs = recommend_songs(user_prefs, songs, k=3)

# Use RAG to explain
for song, score, reasons in recs:
    context = rag.retrieve_song_context(song)
    explanation = rag.generate_recommendation_explanation(
        user_prefs, song, score, reasons, context
    )
    print(f"{song['title']}: {explanation}")
```

### Feature 2: Agentic Workflow

```python
from src.agentic_workflow import RecommendationAgent
from src.recommender import load_songs, Recommender

# Setup
songs = load_songs("data/songs.csv")
recommender = Recommender([])  # Empty for now
agent = RecommendationAgent(recommender)

# Run autonomous workflow
user_prefs = {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False}
recommendations, summary = agent.run(user_prefs, songs)

# Results
print(f"Quality: {summary['final_quality_score']}")
print(f"Iterations: {summary['total_iterations']}")
print(f"Improvement: {summary['quality_improvement']}")
```

### Feature 3: Reliability Testing

```python
from src.reliability_testing import ReliabilityTester
from src.recommender import load_songs

# Setup
songs = load_songs("data/songs.csv")
tester = ReliabilityTester(recommender=None)

# Single test
user_prefs = {"genre": "lofi", "mood": "chill", "energy": 0.4, "likes_acoustic": True}
consistency_result = tester.test_consistency(user_prefs, songs, num_runs=5)
print(f"Consistency: {consistency_result['consistency_score']}")

# Full suite
report = tester.run_full_test_suite(user_prefs, songs)
print(f"Overall: {report['overall_status']}")
```

---

## 🔑 Environment Variables (Optional)

For LLM-enhanced explanations:

```bash
# Claude (Anthropic)
export ANTHROPIC_API_KEY="sk-ant-..."

# OR GPT (OpenAI)
export OPENAI_API_KEY="sk-..."
```

If not set, system uses rule-based explanations automatically.

---

## 📊 Key Metrics

### Agent Quality Score
- Genre match rate (25%)
- Mood match rate (25%)
- Energy alignment (20%)
- Diversity (15%)
- Recommendation score (15%)
- **Pass threshold:** > 0.65

### Test Results
- **Consistency:** Score > 0.60 = PASS
- **Robustness:** Score > 0.40 = PASS
- **Fairness:** No over-rep (< 40%) = PASS
- **Alignment:** Score > 0.50 = PASS

---

## 🧪 Running Tests

```bash
# All AI feature tests
pytest tests/test_ai_features.py -v

# Specific test class
pytest tests/test_ai_features.py::TestMusicRAG -v

# Specific test
pytest tests/test_ai_features.py::TestRecommendationAgent::test_agent_workflow -v

# With coverage
pytest tests/test_ai_features.py --cov=src
```

---

## 📁 Data Format

### User Preferences
```python
{
    "genre": "lofi",           # Primary music type
    "mood": "chill",           # Emotional tone
    "energy": 0.40,            # 0.0 (calm) to 1.0 (intense)
    "target_valence": 0.60,    # 0.0 (sad) to 1.0 (happy)
    "likes_acoustic": True     # Acoustic vs electronic
}
```

### Song Format (from CSV)
```python
{
    "id": 1,
    "title": "Sunrise City",
    "artist": "Neon Echo",
    "genre": "pop",
    "mood": "happy",
    "energy": 0.82,
    "tempo_bpm": 118,
    "valence": 0.84,
    "danceability": 0.79,
    "acousticness": 0.18,
    "popularity": 85,
    "release_decade": "2020s",
    "detailed_mood_tags": ["uplifting", "nostalgic", "euphoric"]
}
```

---

## 🔄 Data Flow Diagram

```
User Input → RAG → Recommender → Agentic Agent → Output
                                       ↓
                             Evaluate & Refine
                                       ↓
                            Reliability Tests
```

---

## ⚙️ Configuration Options

### Scoring Modes (Agent)
```python
"default"           # Genre-first (original)
"mood_first"        # Mood-primary
"energy_focused"    # Energy-dominant
"popularity_aware"  # Considers popularity
```

### Agent Settings
```python
max_iterations = 3          # Max refine attempts
quality_threshold = 0.65    # Pass score
diversity_penalty = False   # Enable artist diversity
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| LLM not working | Check API keys: `echo $ANTHROPIC_API_KEY` |
| Import errors | Run `pip install -r requirements.txt` |
| Tests failing | Ensure `data/songs.csv` exists |
| Low quality score | Agent will auto-retry (up to 3 times) |
| Recommendations repetitive | Enable diversity penalty |

---

## 📝 Common Operations

### Get recommendations with explanations
```python
from src.recommender import recommend_songs
from src.ai_recommender_rag import MusicRAG

songs = load_songs("data/songs.csv")
rag = MusicRAG(songs)
recs = recommend_songs(user_prefs, songs, k=5)

for song, score, reasons in recs:
    explanation = rag.generate_recommendation_explanation(
        user_prefs, song, score, reasons
    )
    print(f"{song['title']}: {explanation}")
```

### Run agent with quality validation
```python
from src.agentic_workflow import RecommendationAgent

agent = RecommendationAgent(recommender)
recs, summary = agent.run(user_prefs, songs)

if summary['final_quality_score'] > 0.70:
    print("High confidence recommendations!")
else:
    print(f"Recommendations improved by {summary['quality_improvement']}")
```

### Validate recommendation consistency
```python
from src.reliability_testing import ReliabilityTester

tester = ReliabilityTester(None)
result = tester.test_consistency(user_prefs, songs, num_runs=5)

if result['status'] == 'PASS':
    print(f"✅ Consistent ({result['consistency_score']})")
else:
    print(f"⚠️ Variable ({result['consistency_score']})")
```

---

## 📞 Support

### Files
- 📖 Full docs: `AI_FEATURES.md`
- 🏗️ Architecture: `IMPLEMENTATION_SUMMARY.md`
- ✅ Requirements: `REQUIREMENTS_FULFILLMENT.md`

### Commands
```bash
python -m src.ai_demo           # Run all demos
pytest tests/test_ai_features.py -v   # Run all tests
python -c "from src.ai_recommender_rag import MusicRAG; help(MusicRAG)"  # API help
```

---

**Version:** 1.0
**Status:** ✅ Production Ready
**Last Updated:** April 24, 2026
