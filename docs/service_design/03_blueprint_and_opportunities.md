# 03 – Service blueprint and opportunities

## 1. Simplified service blueprint

**Flow:** User lands → pastes text → analyses → uses results (and optionally exports or supports).

| Time / flow | Front-stage (user sees) | Back-stage (user doesn’t see) | Support processes |
|-------------|--------------------------|-------------------------------|--------------------|
| **Land** | Browser; single-page app (header, instructions, text area, Analyze). | — | Hosting, asset delivery. |
| **Paste** | Text area; placeholder and copy/paste. | — | — |
| **Analyse** | Button click; “Analyzing…” status. | Tokenisation, vocab extraction, lexicon lookup, frequency scoring, respelling overrides, pronounceability vs Polish inventory. | API (FastAPI), lexicon CSV, global freq, rules (Polish inventory, respelling rules), overrides CSV. |
| **Results** | Table (word, IPA, respelling, local, global, score); coverage bar; phoneme checklist; Download CSV. | Assembly of WordResult (respelling from lexicon or overrides; alreadyPronounceable, unlockedBy). | Same back-stage data. |
| **Export** | CSV download. | Client-side generation from last results. | — |
| **Support** | Support CTA and external payment link. | — | Payment provider (Ko-fi, Stripe, etc.). |

**Key back-stage dependencies:** Lexicon (Oxford 3000 + IPA + respelling), global frequency template, Polish phoneme inventory, respelling overrides. If any fail to load, the API degrades gracefully (empty or partial data).

---

## 2. Front-stage / back-stage boundary

- **Front-stage:** One web page. No login. All value is in the single flow: paste → analyse → read/use/export. Trust is built through clarity, speed, and affirming language (e.g. “sounds you already know”, “you can clearly use X%”).
- **Back-stage:** No user-facing “system” view. Errors surface as status message only. Data (text, word list) is not persisted on the server in the current design; privacy is preserved by design.

**Design principle:** Keep the front-stage simple and positive; keep the back-stage reliable and easy to change (rules, overrides, lexicon) without re-teaching the user.

---

## 3. Pain points and risks (to validate with use)

| Area | Risk / pain | Mitigation (current or planned) |
|------|-------------|----------------------------------|
| **Discovery** | “I don’t know this exists.” | Outreach (schools, teachers, one-pager); optional landing. |
| **First use** | “I’m not sure what to paste or what I’ll get.” | In-page copy (placeholder, small print); consider one-sentence “first time” tip. |
| **Mobile** | Small screen; paste and table usability. | Mobile-first CSS; table scroll; large tap targets. |
| **API down** | “Analyzing…” never resolves or errors. | Clear error message; consider offline or cached fallback later. |
| **Export** | “I don’t know what to do with the CSV.” | Teacher-facing docs (schools explainer); optional “how to use this list” in UI. |
| **Affirmation** | Tool feels like a test or judgment. | Language and framing (coverage as “you can use”, not “you’re missing”); temperament and tone in future layers. |
| **Revenue** | Support CTA ignored. | Low-pressure copy; right moment (after value delivered); optional paywall later. |

---

## 4. Opportunities (prioritised for impact vs effort)

| Opportunity | Impact | Effort | Comment |
|-------------|--------|--------|---------|
| **First-use hint** | Medium | Low | One line or tooltip: “Paste a paragraph from your textbook or any English text.” Reduces hesitation. |
| **Error recovery** | High | Low | Clear, friendly message when API fails; “Try again” or “Check your connection.” |
| **Teacher temperament / customisation** | High | High | Aligns with vision; “how the teacher teaches” and tone. Do after first revenue and some usage data. |
| **Share or save list** | Medium | Medium | Permalink or “Save for later” so teacher/learner can return without re-pasting. |
| **Onboarding flow** | Medium | Medium | Short 2–3 step “what you’ll get” for new visitors. Optional. |
| **Post-export “what next?”** | Medium | Low | E.g. “Use this list for Unit Zero or homework”; link to schools explainer or PDF. |
| **B2B pilot packaging** | High | Medium | One-pager + pilot offer (price, duration, what they get). Enables first B2B revenue. |
| **Evidence-based audit** | High | Medium | After 2–4 weeks of real use: map where drop-off and confusion occur; refine journeys and touchpoints. |

---

## 5. Recommended next steps (aligned with audit)

1. **Ship and learn:** Keep current flow live; drive first revenue (support link, one pilot, or one paid deliverable) and collect feedback.
2. **Harden:** Improve error messaging and, if needed, a first-use hint so the critical path (paste → analyse → use) is robust and clear.
3. **Document for teachers:** Ensure schools explainer and (if needed) a short “how to use the CSV” are easy to find from the app or support flow.
4. **Plan temperament/customisation:** Once you have usage and revenue, use this audit plus evidence to design “teacher temperament” and “how the teacher teaches” without scope creep.
5. **Second audit:** After first revenue and a few weeks of use, run an evidence-based service design audit (where do people stall? what’s missing?) and update journey maps and opportunities.

---

## 6. Links

- [01 Value proposition and actors](01_value_proposition_and_actors.md)
- [02 Journey maps and touchpoints](02_journey_maps_and_touchpoints.md)
- [README](README.md)
