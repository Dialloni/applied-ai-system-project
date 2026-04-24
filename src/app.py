"""
VibeFinder — Streamlit Web Interface
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.recommender import load_songs, recommend_songs
from src.agentic_workflow import RecommendationAgent
from src.recommender import Recommender
from src.reliability_testing import ReliabilityTester
from src.few_shot_specialization import specialized_explanation

st.set_page_config(page_title="VibeFinder", page_icon="🎵", layout="centered")

@st.cache_data
def get_songs():
    return load_songs("data/songs.csv")

SONGS = get_songs()

GENRES = sorted(set(s["genre"] for s in SONGS))
MOODS  = sorted(set(s["mood"]  for s in SONGS))

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🎵 VibeFinder")
st.sidebar.caption("AI-Enhanced Music Recommender")
page = st.sidebar.radio("Navigate", ["Recommend", "Agent Workflow", "Reliability Tests", "Few-Shot Tones"])

# ── Page: Recommend ───────────────────────────────────────────────────────────
if page == "Recommend":
    st.title("🎵 Find Your Vibe")
    st.write("Set your taste preferences and get personalized song picks.")

    col1, col2 = st.columns(2)
    with col1:
        genre = st.selectbox("Favorite Genre", GENRES, index=GENRES.index("lofi") if "lofi" in GENRES else 0)
        mood  = st.selectbox("Current Mood",   MOODS,  index=MOODS.index("chill") if "chill" in MOODS else 0)
    with col2:
        energy       = st.slider("Energy Level",  0.0, 1.0, 0.5, 0.05)
        likes_acoustic = st.checkbox("Prefer Acoustic Sound", value=False)

    mode = st.selectbox("Scoring Mode", ["default", "mood_first", "energy_focused", "popularity_aware"])
    diversity = st.checkbox("Diversity Penalty (avoid repeat artists)", value=False)
    k = st.slider("Number of Results", 3, 10, 5)

    if st.button("🔍 Get Recommendations", type="primary"):
        prefs = {"genre": genre, "mood": mood, "energy": energy, "likes_acoustic": likes_acoustic}
        recs  = recommend_songs(prefs, SONGS, k=k, mode=mode, diversity_penalty=diversity)

        st.subheader(f"Top {k} Songs for You")
        for i, (song, score, reasons) in enumerate(recs, 1):
            genre_match = "✅" if song["genre"] == genre else "⬜"
            mood_match  = "✅" if song["mood"]  == mood  else "⬜"
            with st.expander(f"#{i}  {song['title']} — {song['artist']}  |  Score: {score:.2f}  {genre_match}{mood_match}"):
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Genre", song["genre"])
                col_b.metric("Mood",  song["mood"])
                col_c.metric("Energy", f"{song['energy']:.2f}")
                st.caption("Why recommended:")
                for r in reasons:
                    st.write(f"• {r}")

# ── Page: Agent Workflow ──────────────────────────────────────────────────────
elif page == "Agent Workflow":
    st.title("🤖 Agentic Workflow")
    st.write("Watch the AI plan, act, evaluate, and self-correct to find your best match.")

    col1, col2 = st.columns(2)
    with col1:
        genre  = st.selectbox("Genre",  GENRES)
        mood   = st.selectbox("Mood",   MOODS)
    with col2:
        energy = st.slider("Energy", 0.0, 1.0, 0.7, 0.05)

    if st.button("▶ Run Agent", type="primary"):
        prefs = {"genre": genre, "mood": mood, "energy": energy}

        with st.spinner("Agent running Plan → Act → Evaluate → Refine..."):
            agent = RecommendationAgent(Recommender([]))
            recs, summary = agent.run(prefs, SONGS)

        quality    = summary.get("final_quality_score", 0.0)
        iterations = summary.get("total_iterations", 0)
        # re-evaluate to get metrics
        _, evaluation = agent.evaluate(recs, prefs)
        metrics = evaluation.get("metrics", {})

        # Quality gauge
        color = "green" if quality >= 0.65 else "orange" if quality >= 0.45 else "red"
        st.markdown(f"### Quality Score: :{color}[{quality:.2f}]")
        st.progress(float(quality))
        st.caption(f"Completed in {iterations} iteration(s) · threshold = 0.65")

        if metrics:
            st.subheader("Evaluation Metrics")
            cols = st.columns(len(metrics))
            for col, (k_m, v_m) in zip(cols, metrics.items()):
                col.metric(k_m.replace("_", " ").title(), f"{v_m:.2f}")

        st.subheader("Recommended Songs")
        for i, (song, score, reasons) in enumerate(recs, 1):
            with st.expander(f"#{i}  {song['title']} — {song['artist']}  (score: {score:.2f})"):
                st.write(", ".join(reasons[:3]))

# ── Page: Reliability Tests ───────────────────────────────────────────────────
elif page == "Reliability Tests":
    st.title("✅ Reliability Testing")
    st.write("Verify the AI gives consistent, robust, and fair results.")

    col1, col2 = st.columns(2)
    with col1:
        genre  = st.selectbox("Test Genre", GENRES)
        mood   = st.selectbox("Test Mood",  MOODS)
    with col2:
        energy = st.slider("Energy", 0.0, 1.0, 0.5, 0.05)

    if st.button("🧪 Run Tests", type="primary"):
        prefs  = {"genre": genre, "mood": mood, "energy": energy}
        tester = ReliabilityTester(SONGS)

        with st.spinner("Running reliability suite..."):
            report = tester.run_full_test_suite(prefs, SONGS)

        overall = report.get("overall_status", "UNKNOWN")
        passed  = report.get("tests_passed", 0)
        total   = report.get("tests_run", 0)

        if overall == "PASS":
            st.success(f"Overall: PASS — {passed}/{total} tests passed")
        else:
            st.error(f"Overall: {overall} — {passed}/{total} tests passed")

        # Individual test results
        for key in ["consistency", "robustness", "fairness", "explanation_alignment"]:
            result = report.get(key)
            if result is None:
                continue
            status = result.get("status", "SKIP")
            icon   = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭"
            with st.expander(f"{icon} {key.replace('_', ' ').title()} — {status}"):
                for k_r, v_r in result.items():
                    if k_r not in ("test_name", "status"):
                        st.write(f"**{k_r}:** {v_r}")

# ── Page: Few-Shot Tones ──────────────────────────────────────────────────────
elif page == "Few-Shot Tones":
    st.title("🎭 Few-Shot Specialization")
    st.write("Same song recommendation — three specialized tones showing measurable output difference.")

    col1, col2 = st.columns(2)
    with col1:
        genre  = st.selectbox("Genre", GENRES, index=GENRES.index("lofi") if "lofi" in GENRES else 0)
        mood   = st.selectbox("Mood",  MOODS,  index=MOODS.index("chill") if "chill" in MOODS else 0)
    with col2:
        energy = st.slider("Energy", 0.0, 1.0, 0.4, 0.05)

    if st.button("🎨 Generate Tones", type="primary"):
        prefs = {"genre": genre, "mood": mood, "energy": energy}
        recs  = recommend_songs(prefs, SONGS, k=3)

        for i, (song, score, reasons) in enumerate(recs, 1):
            st.markdown(f"---\n**#{i} {song['title']}** by {song['artist']} — Score: {score:.2f}")

            col_a, col_b, col_c = st.columns(3)

            baseline = specialized_explanation(song, score, reasons, "baseline")
            chill    = specialized_explanation(song, score, reasons, "chill_student")
            hype     = specialized_explanation(song, score, reasons, "hype_coach")

            with col_a:
                st.markdown("**📋 Baseline**")
                st.info(baseline)
            with col_b:
                st.markdown("**😎 Chill Student**")
                st.success(chill)
            with col_c:
                st.markdown("**💪 Hype Coach**")
                st.warning(hype)
