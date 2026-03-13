### ClearPronounce – Working Roadmap (Disciplined Entrepreneurship flavoured)

This roadmap is structured in three layers:

- **Strategic goals (WHY, long-term)** – big outcomes we’re aiming for.  
- **Tactical objectives (WHAT, 1–3 months)** – bundles of work that move those goals.  
- **Operational tasks (HOW, 1–2 weeks)** – concrete items we actually implement.

It loosely reflects themes from **Disciplined Entrepreneurship** (Bill Aulet): start with a specific beachhead, understand your end user deeply, focus on a clear value prop, and iterate with evidence.

---

### 1. Strategic goals (WHY)

**S1. Prove that ClearPronounce improves Polish learners’ intelligibility in English.**  
Evidence: small but solid data from 100+ Polish learners that your respellings + hints make their English **easier to understand** (especially on â, th‑sounds, and schwa).

**S2. Make ClearPronounce part of weekly lesson prep for Polish English teachers.**  
Evidence: at least 5–10 teachers using it regularly on real texts, saying it saves prep time and helps them plan pronunciation work more systematically.

**S3. Build a reusable “sound‑profile engine” that can support multiple user types and L1s.**  
Evidence: the backend can represent different profiles (e.g. Polish learner, Polish teacher) and, later, other L1s, without rewriting the core engine.

---

### 2. Tactical objectives (WHAT)

#### T1. Polish learner profile v1 is solid and testable (under S1 & S3)

Goal: A well‑defined `pl_learner` profile (core sounds, respelling rules, stress behaviour) that works well enough to expose to 100 learners.

- **Key design choices (informed by ELF and your Polish knowledge):**
  - Core unlock sounds for this profile: `/θ, ð, ŋ, ʌ, ə`.
  - Advanced but *not* core for now: `/æ, ɝ/` (may appear later in an “advanced” section).
  - CMUdict remains the backbone for phonemes + stress (AH0→ə, AH1/2→ʌ, etc.).
  - Respelling layer may over‑pronounce for clarity:
    - `/ʌ/` → `â` (STRUT vowel, e.g. *but, some, come, young, country*).
    - Pre‑stress word‑initial `/ə/` in content words (e.g. *about, again, ago*) generally → `a` in careful respelling, not `ə`.
  - Stress highlighting:
    - Bold + UPPERCASE only when stress is pedagogically interesting.
    - No bold/caps in monosyllables or words with penultimate stress.
    - Bold/cap when primary stress is on an earlier syllable (e.g. *aBILity, COMfortable*).

#### T2. 100‑learner respelling test completed and analysed (under S1)

Goal: A small, focused online test where Polish learners judge clarity and usefulness of your respellings on a curated set of words (especially those with `/ʌ/` and `/ə/`), and you update HYPOTHESES accordingly.

#### T3. Teacher adoption loop started (under S2)

Goal: Talk to Polish EFL teachers, watch them use the tool on their own lesson texts, and refine the product so it fits seamlessly into lesson prep.

#### T4. Profiles generalised beyond a single hard‑coded case (under S3)

Goal: Introduce a configurable profile system in the backend so adding “Polish teacher” or another L1 later is mostly a data/config change.

---

### 3. Operational tasks (HOW, near-term)

These are the concrete steps we’re working on now, mapped to tactical objectives.

#### Under T1 – Polish learner profile v1

- **Respelling audit for key /ʌ/ and schwa words**
  - Lock in desired respellings for a small, high‑impact set:
    - `/ʌ/` words: *but, some, come, must, much, young, country, other, love, up, number, under, another…*
    - Pre‑stress schwa words: *about, again, ago, around, because, above…*
  - Encode the resulting decisions as small, general rules (position‑based where possible) rather than one‑off overrides.

- **Profile concept in the backend**
  - Introduce a simple `pl_learner` profile that defines:
    - `always_known_phonemes`.
    - `core_unlock_phonemes`.
    - Any profile‑specific respelling tweaks or stress rules.
  - Make `/analyze-text` take an optional `profile` parameter (defaulting to `pl_learner` for now).

#### Under T2 – 100‑learner respelling test

- Freeze a “testable” version of:
  - CMU→IPA mapping.
  - Respelling rules for the audited words.
  - Core sound list.
- Design a short online task (e.g. Google Form) where Polish learners:
  - See spelling + respelling (and optionally IPA) for a handful of target words.
  - Rate clarity and usefulness, and maybe do a few simple discrimination tasks.

#### Under T3 – Teacher adoption loop

- Use the current prototype on real teacher texts:
  - Observe how they interpret the table and the “sounds” checklist.
  - Identify 1–2 small features that make the output more “lesson‑shaped” (e.g. mini plan summary, class‑view list).

#### Under T4 – Profiles beyond Polish learners

- Sketch what a `pl_teacher` profile would change (e.g. more IPA, less respelling, different defaults for “sounds my class is OK with”).
- Ensure the profile system is general enough that adding this later is mostly configuration.

---

### 4. Future / parking lot (LATER)

- **Intake process**
  - Short, learner‑facing intake that:
    - Asks a few targeted questions / tasks to infer which core sounds they already control.
    - Produces a sound profile that the analyzer and guides respect (only teaching truly new sounds).

- **G2P fallback for OOV words**
  - Integrate a grapheme‑to‑phoneme engine (e.g. OpenPhonemizer / Phonetisaurus / eSpeak NG) as a fallback when CMUdict has no entry.
  - Map its output into the existing IPA inventory and respelling rules, so the system can handle names and novel words.

- **Additional L1 profiles**
  - After Polish→English is working and tested, consider adding another L1→English (or L1→Polish) profile (e.g. Ukrainian learners in Poland).

- **Corpus / recordings**
  - Longer‑term research idea: small, focused recordings of Polish learners and proficient ELF users on key sounds (`â`, schwa, th‑sounds) to refine rules and examples.

- **Maybe: gradually teach IPA through the unlock process**
  - Idea: as learners “unlock” each new sound (â, θ, ð, ŋ, ə), optionally introduce the corresponding IPA symbol alongside the respelling, so over time they learn IPA by use rather than in one go. Unclear if it adds value or cognitive load; keep as a maybe until we have learner feedback.

