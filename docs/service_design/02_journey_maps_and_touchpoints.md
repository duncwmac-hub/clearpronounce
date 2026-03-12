# 02 – Journey maps and touchpoints

## 1. Journey map – Teacher (primary flow)

**Actor:** Teacher or trainer preparing materials for a lesson or Unit Zero.

| Phase | Actions | Touchpoints | Thoughts / feelings (to validate) |
|-------|---------|-------------|-----------------------------------|
| **Discover** | Hears about ClearPronounce (colleague, search, referral). | Word of mouth, web, social, school contact. | “I need something that works with my existing materials.” |
| **Land** | Opens the app (URL or link). | Web app (browser). | “Is this for me? Can I use it with my textbook?” |
| **Prepare input** | Gets text (coursebook scan, PDF copy, meeting notes). Pastes into text area. | Phone/tablet (OCR, copy), laptop; ClearPronounce text area. | “I hope this doesn’t take long.” |
| **Analyse** | Clicks “Analyze”. Waits for response. | Analyze button, status message, API. | “Fast enough?” |
| **Use results** | Reads table (word, IPA, respelling, local/global, score). Uses coverage bar and phoneme checklist. Optionally downloads CSV. | Results table, coverage %, phoneme checkboxes, Download CSV. | “Which words do I assign? Which sounds should we drill?” |
| **Export / reuse** | Saves or shares CSV; uses it in lesson prep or LMS. | CSV file, email, drive, printer. | “I have something I can use tomorrow.” |
| **Support (optional)** | Clicks “Support ClearPronounce” or ignores. | Support CTA, payment link. | “Worth a few euros if it keeps improving.” |

**Critical path:** Land → Prepare input → Analyse → Use results. Export and Support are value multipliers.

---

## 2. Journey map – Learner (primary flow)

**Actor:** Polish-speaking learner (e.g. professional or student) using the same tool, possibly sent by teacher or found on their own.

| Phase | Actions | Touchpoints | Thoughts / feelings (to validate) |
|-------|---------|-------------|-----------------------------------|
| **Discover** | Teacher shares link or learner searches for pronunciation help. | Teacher, search, link. | “I want to sound clearer.” |
| **Land** | Opens the app. | Web app (often mobile). | “Is this going to judge me?” |
| **Prepare input** | Pastes text (from homework, meeting, or email). | Phone/laptop; ClearPronounce text area. | “I hope it’s simple.” |
| **Analyse** | Taps “Analyze”. | Analyze button, status, API. | “Quick?” |
| **Use results** | Reads respellings; uses coverage bar; ticks “I already know this” for sounds. | Table (word, IPA, respelling), coverage %, phoneme checkboxes. | “I can see what I already have and what’s new. Feels affirming.” |
| **Practice (future)** | Uses list for self-study or in class. | Printed list, screen, future practice/audio. | “I know what to work on.” |
| **Support (optional)** | Considers supporting. | Support CTA. | “I’d chip in if it helps.” |

**Critical path:** Land → Prepare input → Analyse → Use results. Affirmation is a design requirement (language, framing, no “deficit” tone).

---

## 3. Touchpoint inventory

| Touchpoint | Owner | Stage | Notes |
|------------|--------|-------|--------|
| **Web app (single page)** | Product | Land, Prepare, Analyse, Use results | Primary interface. Mobile-first. |
| **Analyze button + status** | Product | Analyse | Must feel responsive; errors must be clear. |
| **Results table** | Product | Use results | Word, IPA, respelling, local, global rank, score. |
| **Coverage bar + phoneme checklist** | Product | Use results | “You can clearly use X%”; checkboxes for “I already know this sound.” |
| **Download CSV** | Product | Use results / Export | Teacher-oriented; includes alreadyPronounceable, unlockedBy. |
| **Support CTA** | Product | Support | Link to Ko-fi / Stripe etc. Low pressure. |
| **API (POST /analyze-text)** | Backend | Analyse | Invisible to user; must be stable and fast. |
| **CSV file** | Product | Export | Offline artefact; used in prep or LMS. |
| **Word of mouth / referral** | Marketing / school | Discover | Not built in product; part of service. |
| **Landing / discovery page** | Marketing | Discover | Currently minimal; could be same app or separate. |

**Gaps (candidates for later):** Onboarding (first-time explanation), error recovery, “Share this list” or permalink, and any post-download “what next?” (e.g. Unit Zero reminder).

---

## 4. Cross-actor flow (teacher → learner)

1. Teacher discovers and uses ClearPronounce; exports CSV or shares link.
2. Teacher assigns text or list to learners (e.g. “Paste this paragraph and check your coverage”).
3. Learner uses same app, possibly with teacher’s text or their own.
4. Value to learner: clarity on which sounds matter for this text; affirmation via coverage game.
5. Value to teacher: less prep; learners arrive with clearer pronunciation focus.

The same touchpoints serve both; differentiation (e.g. “teacher temperament”, customisation) will layer on top of this shared journey.
