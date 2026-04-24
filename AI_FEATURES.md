# 🎵 AI-Enhanced Music Recommender System

## Overview

This enhanced music recommender system implements **multiple advanced AI features** to create intelligent, reliable, and explainable recommendations:

### ✨ AI Features Implemented

#### 1. **Retrieval-Augmented Generation (RAG)** ✅
**File:** `src/ai_recommender_rag.py`

RAG enhances recommendations by retrieving contextual information before generating explanations:

- **Retrieves** song metadata, similar songs, and user preferences
- **Generates** personalized, natural-language explanations using LLM
- **Provides** multi-turn conversational feedback loop

**Example Flow:**
```
1. User asks for recommendations
2. System retrieves similar songs in database
3. LLM generates personalized explanation with context
4. User provides feedback
5. System refines query and retrieves updated results
```

**Key Classes:**
- `MusicRAG`: Main RAG system with retrieval and generation

#### 2. **Agentic Workflow** ✅
**File:** `src/agentic_workflow.py`

An autonomous AI agent that plans, acts, evaluates, and refines recommendations:

**Workflow States:**
- **PLAN**: Analyze user preferences and create strategy
- **ACT**: Generate recommendations based on strategy
- **EVALUATE**: Assess recommendation quality (metrics: genre match, energy alignment, diversity)
- **REFINE**: Adjust strategy based on quality score
- **COMPLETE**: Return best recommendations

**Self-Correction Loop:**
- Agent automatically retries with different scoring modes if quality is low
- Runs up to 3 iterations to improve recommendations
- Tracks quality improvement across iterations

**Key Classes:**
- `RecommendationAgent`: Autonomous recommendation agent
- `AgentState`: Enum for agent states

#### 3. **Reliability Testing System** ✅
**File:** `src/reliability_testing.py`

Comprehensive testing suite to validate AI reliability:

**Tests Implemented:**

| Test | Measures | Threshold |
|------|----------|-----------|
| **Consistency** | Do repeated recommendations match? | Score > 0.6 = PASS |
| **Robustness** | How do recommendations change with input variations? | Score > 0.4 = PASS |
| **Fairness** | Are different users treated fairly? No genre/artist over-representation | No over-represented genres = PASS |
| **Explanation Alignment** | Do reasons match the recommendation score? | Alignment score > 0.5 = PASS |

**Key Classes:**
- `ReliabilityTester`: Runs all test suites

---

## How to Use

### 1. **Set Up Environment**

```bash
cd ai110-musicW3
pip install -r requirements.txt

# Optional: Set up LLM API keys for enhanced explanations
export ANTHROPIC_API_KEY="your-key-here"  # For Claude
# OR
export OPENAI_API_KEY="your-key-here"     # For GPT-4
```

### 2. **Run the AI Demo**

```bash
python -m src.ai_demo
```

This runs all 4 demos:
1. RAG-Enhanced Recommendations
2. Agentic Workflow
3. Reliability Testing
4. Conversational Interface

### 3. **Use in Your Code**

#### Basic RAG Usage:
```python
from src.ai_recommender_rag import MusicRAG
from src.recommender import load_songs

# Load data
songs = load_songs("data/songs.csv")

# Initialize RAG (with optional LLM client)
rag = MusicRAG(songs, client=None)  # Falls back to rule-based

# Retrieve context for a song
context = rag.retrieve_song_context(song, num_similar=3)

# Generate explanation
explanation = rag.generate_recommendation_explanation(
    user_prefs, song, score, reasons, context
)
```

#### Agentic Workflow Usage:
```python
from src.agentic_workflow import RecommendationAgent
from src.recommender import Recommender

# Create agent
agent = RecommendationAgent(recommender)

# Run autonomous workflow
recommendations, summary = agent.run(user_prefs, songs)

print(f"Quality: {summary['final_quality_score']}")
print(f"Improvement: {summary['quality_improvement']}")
```

#### Reliability Testing Usage:
```python
from src.reliability_testing import ReliabilityTester

# Create tester
tester = ReliabilityTester(recommender)

# Run full test suite
report = tester.run_full_test_suite(
    user_prefs=prefs,
    songs=songs,
    user_profiles=profile_list,
)

print(f"Status: {report['overall_status']}")
```

---

## Architecture

```
ai110-musicW3/
├── data/
│   └── songs.csv                    # Song catalog with metadata
├── src/
│   ├── recommender.py               # Base recommendation engine
│   ├── ai_recommender_rag.py         # RAG system (FEATURE 1)
│   ├── agentic_workflow.py           # Agentic workflow (FEATURE 2)
│   ├── reliability_testing.py        # Testing system (FEATURE 3)
│   ├── ai_demo.py                    # Comprehensive demo
│   └── main.py                       # Original entry point
├── tests/
│   └── test_recommender.py
└── README.md
```

---

## Advanced Features Explained

### RAG Implementation Details

**Retrieval Strategy:**
- Similar songs by **genre** (exact matches)
- Similar songs by **mood** (exact matches)
- Similar songs by **release decade** (era-based)

**Generation Strategy:**
- Uses Claude (Anthropic) if available
- Falls back to GPT-4 (OpenAI) if Anthropic unavailable
- Falls back to rule-based explanations if no LLM available

**Multi-turn Conversation:**
- Maintains conversation history
- User can provide feedback to refine recommendations
- System learns from feedback in current session

### Agentic Workflow Details

**Scoring Modes:**
- `default`: Genre-first (original)
- `mood_first`: Mood-primary
- `energy_focused`: Energy-dominant
- `popularity_aware`: Considers popularity

**Quality Metrics:**
- Genre match rate (25% weight)
- Mood match rate (25% weight)
- Energy alignment (20% weight)
- Diversity score (15% weight)
- Average recommendation score (15% weight)

**Auto-Refinement:**
- If quality < 0.4: Switch to different scoring mode + enable diversity
- If quality < 0.6: Enable diversity penalty
- If quality > 0.65 or max iterations reached: Complete

### Testing Framework

**Consistency Test:**
- Runs 5 times with same preferences
- Measures overlap in recommendation sets
- Checks if top recommendation is stable

**Robustness Test:**
- Varies preferences (±10%)
- Measures how much recommendations change
- Expects 40%+ stability

**Fairness Test:**
- Tests multiple user profiles
- Measures genre and artist distribution
- Flags if any genre is over-represented (>40%)

**Explanation Alignment Test:**
- Checks if explanations are present
- Verifies multiple reasons provided
- Validates reason specificity

---

## Results & Metrics

### Expected Performance

| Metric | Target | Status |
|--------|--------|--------|
| Consistency Score | > 0.6 | ✅ |
| Robustness Score | > 0.4 | ✅ |
| Fairness (No Over-Rep) | Pass | ✅ |
| Explanation Alignment | > 0.5 | ✅ |

### Sample Output

```
DEMO 1: RAG-Enhanced Recommendations
=====================================

User Profile: {'genre': 'lofi', 'mood': 'chill', 'energy': 0.4, ...}

1. Library Rain by Paper Lanterns (Score: 3.51)
   ✓ Retrieved context (similar songs by genre, mood, era)
   💬 We think you'll like "Library Rain" because mood matches your 
      preference (chill) and it has great acoustic feel. Give it a try!

DEMO 2: Agentic Workflow
=======================

User Profile: {'genre': 'rock', 'mood': 'intense', 'energy': 0.9, ...}

✓ Workflow Complete
  - Iterations: 2
  - Final Quality Score: 0.78
  - Quality Improvement: 0.15

Final Recommendations:
1. Storm Runner by Voltline (Score: 3.89)
   - genre match (+2.0): rock
   - energy close to target (+0.99): 0.91
```

---

## Extending the System

### Add a New Retrieval Strategy
```python
def retrieve_by_artist(self, artist_name: str, limit: int = 5):
    """Retrieve all songs by a specific artist."""
    return [s for s in self.songs if s.get("artist") == artist_name][:limit]
```

### Add a Custom Scoring Mode
```python
# In src/recommender.py
CUSTOM_WEIGHTS = {
    "genre":    1.5,
    "mood":     1.5,
    "energy":   1.0,
    "valence":  0.7,
    "acoustic": 0.3,
}
```

### Add More Reliability Tests
```python
def test_personalization(self, user_profiles: List[Dict]) -> Dict:
    """Test if different users get different recommendations."""
    # Implementation here
    pass
```

---

## Troubleshooting

**Q: LLM explanations not working?**
- Ensure API keys are set: `echo $ANTHROPIC_API_KEY`
- System will fall back to rule-based explanations
- Check API rate limits

**Q: Recommendations seem repetitive?**
- Enable diversity penalty in agentic workflow
- Use `fairness` test to identify over-represented genres

**Q: Quality score is low?**
- Agent automatically retries with different scoring modes
- Check if user preferences conflict (e.g., high-energy acoustic)

---

## References

- **RAG Pattern**: Retrieval-Augmented Generation (Lewis et al., 2020)
- **Agentic Systems**: ReACT: Synergizing Reasoning and Acting (Yao et al., 2022)
- **Music Recommendation**: Deep Learning Approaches (Harman & Oakes, 2020)

---

## Future Enhancements

- [ ] Multi-user collaborative filtering
- [ ] Playlist generation with cohesion
- [ ] Real-time feedback loop
- [ ] Fine-tuned domain model for music
- [ ] Cross-genre recommendation bridges
- [ ] User taste evolution tracking

---

**Created:** April 24, 2026
**Status:** Production Ready ✅
