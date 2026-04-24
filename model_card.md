# Model Card: Music Recommender Simulation

## 1. Model Name

### VibeFinder 1.0

---

## 2. Goal / Task

Suggest 5 songs from a catalog that match what a listener says they like. The system takes a user's taste profile (genre, mood, energy level) and finds the best matches based on scoring rules.

**What it predicts:** Which songs will be most appealing to a user based on their stated preferences.

**What it doesn't predict:** Whether you'll actually enjoy the song, if you'll skip it, or if you'll come back to it later.

---

## 3. Intended Use and Non-Intended Use

**Intended Use:**

- Classroom project to learn how recommendation algorithms work
- Exploring how simple math can produce "intelligent-seeming" suggestions
- Testing how algorithm design choices affect recommendations
- Understanding where bias shows up in AI systems

**Non-Intended Use:**

- Do NOT use this for real music recommendations — it's too simple and limited
- Do NOT deploy this as a real product — it only has 20 songs
- Do NOT use it to make decisions about music services or licensing
- Do NOT assume it's fair to all listeners — it clearly favors certain genres

---

## 4. Algorithm Summary (Plain Language)

The system scores each song by asking: "How well does this match what the user wants?"

**The Scoring Rule (for one song):**

- **Genre match:** +2.0 points if the song's genre matches (e.g., user wants pop, song is pop)
- **Mood match:** +1.0 points if the song's mood matches (e.g., user wants happy, song is happy)
- **Energy closeness:** up to +1.0 points based on how close the song's energy is to the user's target
- **Valence (positivity):** up to +0.5 points based on how close the song's valence is to the user's target
- **Acoustic preference:** up to +0.5 points based on whether the user likes acoustic or produced sounds

All points are added up. The song with the highest total score is ranked #1, the second-highest is #2, and so on.

**Why these weights?** Genre is worth the most because it's the biggest deal — a jazz fan won't be happy with a pop song no matter what. Mood matters next. Energy and valence are smaller tweaks that distinguish songs within a genre.

---

## 5. Data Used

**Dataset size:** 20 songs total.

**Features per song:** genre, mood, energy (0-1), tempo, valence (0-1), danceability (0-1), acousticness (0-1).

**Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, classical, country, r&b, metal, folk, reggaeton, blues, edm, k-pop.

**Moods represented:** happy, chill, intense, relaxed, moody, focused, confident, peaceful, romantic, aggressive, melancholic, euphoric, sad.

**Limits and concerns:**

- Most genres only have 1-2 songs. This is a huge limit.
- The song titles and artists are made up — this is synthetic data, not real music.
- No songs represent some popular genres (e.g., only one classical song, one blues song).
- No information about who actually enjoys these songs or listening patterns.
- The dataset has no diversity — all fictional artists and no demographic representation.

---

## 6. Strengths

- Works well for users who have a clear genre and mood preference — they get results that match their stated taste immediately.
- The energy scoring gives it some nuance beyond simple category matching: a pop song with the wrong energy will score lower than one with the right energy.
- The explanation output makes the system transparent — users can see exactly why a song was picked.
- Simple enough to fully understand and reason about.

---

## 7. Observed Behavior and Biases

**The biggest bias:** Genre is king. Because genre is worth +2.0 points and everything else maxes out around +0.5-1.0, the system pre-filters by genre before anything else matters. If you like rock, you'll get rock songs even if they don't match your mood or energy.

**The conflicting-preference problem:** When a user wants "high-energy blues," the only blues song (Midnight Delta) scores highest even though it's actually low-energy (0.36). The system picked the best genre match but completely failed the energy request. This happens silently — the user doesn't know the system couldn't satisfy both preferences.

**The genre-gap problem:** If your favorite genre isn't in the catalog at all (like reggae), the system falls back to mood and energy — but those alone don't make sense. A jazz song gets recommended just because the mood happened to match, not because it's actually a good substitute for reggae.

**The exact-match trap:** "Indie pop" and "pop" get zero credit toward each other even though they're similar. The system only understands exact string matches.

**What this means in practice:** Users whose taste matches the catalog's genres get great recommendations. Users with niche or underrepresented taste get frustrating results or nothing useful.

---

## 8. Evaluation Process

**How I tested:** I created 5 user profiles (3 normal + 2 intentionally tricky) and ran them through the system to see what happened.

**Profile 1 (High-Energy Pop):** Works great. Sunrise City ranked #1 — matches genre, mood, energy, everything. This is the "happy path" where the system does what it's supposed to do.

**Profile 2 (Chill Lofi):** Also works great. Library Rain and Midnight Coding both hit all the signals. The acoustic bonus helped push lofi songs ahead of other genres. Results felt exactly right.

**Profile 3 (Deep Intense Rock):** Surprising behavior. Storm Runner (#1) was perfect, but Neon Pulse (EDM) and Gym Hero (Pop) ranked above Shatterpoint (metal). Why? Because they matched the "intense" mood and high energy, even though EDM and Pop are nothing like rock. The genre signal wasn't strong enough to filter these out.

**Profile 4 (High-Energy Blues — conflicting):** System failed quietly. Midnight Delta (the only blues song) ranked #1, but it's actually low-energy (0.36), not high-energy (0.9). The user gets a blues song but not what they asked for. The huge score gap (#1 = 4.32, #2 = 1.41) shows the system thinks it found a perfect answer when it didn't.

**Profile 5 (Reggae — not in catalog):** Zero genre matches. Coffee Shop Stories (jazz) ranked #1 only because "relaxed" mood matched. The results feel random. This proves genre is load-bearing — without it, the scores don't mean much.

**Experiment:** I halved the genre weight (2.0 → 1.0) and doubled the energy weight (1.0 → 2.0). Result: same top songs, but smaller score gaps. High-energy songs from other genres became more competitive. This shows genre was doing 80% of the filtering work in the original setup.

**Conclusion:** The system works well for mainstream tastes and clear preferences, but silently fails for conflicting preferences or underrepresented genres.

---

## 9. Ideas for Improvement

If I kept working on this, I'd try:

1. **Let users adjust weights.** Add a slider so users can say "energy matters more than genre to me." The code already supports this (`weights` parameter), just need a UI.

2. **Bigger, more balanced catalog.** With 500+ songs and 50+ per genre, the system would work better for niche tastes. Right now, 1-2 songs per genre is way too small.

3. **Add listening history.** Stop recommending the same songs every time. Track what you've already heard and remove those from the top 5.

4. **Hybrid approach.** Don't just score within a user's genre. Show some variety — recommend 3 songs from their favorite genre, then 1-2 from adjacent genres or high-energy alternatives.

---

## 10. Personal Reflection

**My biggest learning moment:**

The moment I realized that bias lives in the data, not the algorithm. I built what I thought was a "fair" system — it scores songs consistently, applies the same rules to everyone, and picks the best matches. But then I tested a reggae user (a genre not in the catalog) and watched the system return jazz and k-pop songs in a seemingly random order. It wasn't biased in how it calculated scores. It was biased because the catalog itself didn't represent reggae at all. The system was working "correctly" while still failing an entire group of users. That's terrifying when you think about real AI systems used by millions of people.

**Where I needed to double-check the AI:**

The code Claude generated was solid, but I had to verify the scoring math myself. I wanted to make sure the proximity formula (1.0 - abs(difference)) actually rewarded closeness the way I intended. Also, when I changed the weights for the experiment, I manually traced through a few examples to confirm the rankings would shift the way the code predicted. Don't blindly trust generated code — understand it first.

**What surprised me about simple algorithms:**

I expected the system to feel dumb. Instead, it feels oddly smart. When I see "Sunrise City" ranked #1 for a pop/happy user with a score of 4.82, with reasons like "genre matches (pop), mood matches (happy), energy close to target" — it looks intelligent. It looks like it "understands" music taste. But it doesn't. It's just matching numbers. That's wild. This is probably why people trust recommenders so much — they hide their simplicity behind good UI and accurate results (for the majority case). A casual user would never know that a reggae listener is getting garbage recommendations.

**What I'd try next:**

I want to build the same system but with real music data and real listening patterns. Grab 10,000 songs from a music API, build user profiles from actual Spotify listeners, and see if the simple scoring approach still works at scale. I suspect the "conflicting preferences" problem would get even worse with real data — you'd have users asking for high-energy classical or sad danceable music, which are real preferences but rare. I'd also like to add collaborative filtering: "users who like X also liked Y," which is what real recommenders use to discover niche stuff. The pure content-based approach has a ceiling.

**Final thought:**

Building this made me realize that "AI" recommendations are often just clever math on top of biased data. The math isn't the problem. The problem is: whose data? What genres did we collect? What moods did we label? If the data is biased, no algorithm can fix that. You need representative data first.
