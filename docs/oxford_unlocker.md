## Oxford 3000 + unlocker pipeline

This note explains how we use the Oxford 3000 dataset together with CMUdict and the unlocker logic to identify words that are fully pronounceable with the current Polish phoneme inventory, starting from level A1.

### Data sources

- `data/Oxford3000_Vocab-main/oxford3000_vocabulary_with_collocations_and_definitions_datasets.csv`
  - Columns include `Word`, `Definition`, `Example Sentence`, `Part of Speech`, etc.
- `data/CMUdict/cmudict.dict`
  - Source of ARPABET pronunciations for English words.
- `rules/phonemes_english.md` and `rules/phonemes_polish.md`
  - Canonical English and Polish phoneme inventories.
- `rules/english_to_polish_respellings.md`
  - Mapping from English phonemes to Polish-like respellings.
- `data/oxford_levels.csv`
  - Placeholder CSV (`word,level`) for CEFR levels (A1, A2, ...). Needs to be filled from an external Oxford 3000 level list before A1 filtering will yield non-empty results.

### Pipeline steps

1. **Build Oxford lexicon**
   - Script: `lexicon/build_oxford_lexicon.py`
   - Command (example):
     - `python3 -m lexicon.build_oxford_lexicon --oxford data/Oxford3000_Vocab-main/oxford3000_vocabulary_with_collocations_and_definitions_datasets.csv --cmudict data/CMUdict/cmudict.dict --levels data/oxford_levels.csv --out lexicon/lexicon_oxford3000.csv`
   - Output: `lexicon/lexicon_oxford3000.csv` with columns:
     - `word` (lowercased, single-word entries only)
     - `ipa` (from CMU ARPABET via `arpabet_to_ipa`)
     - `cmu_pron`
     - `phoneme_set` (as in the main lexicon)
     - `polish_respellings` (via `generate_respelling(ipa)`)
     - `pos`
     - `frequency_rank` (simple running index)
     - `level` (from `oxford_levels.csv` or `"unknown"` if not provided)
     - `definition`
     - `example_sentence`

2. **Run unlocker**
   - Script: `lexicon/unlocker.py`
   - Command (example):
     - `python3 lexicon/unlocker.py --lexicon lexicon/lexicon_oxford3000.csv --english rules/phonemes_english.md --polish rules/phonemes_polish.md --out lexicon/lexicon_oxford3000_unlocks.csv`
   - Output: `lexicon/lexicon_oxford3000_unlocks.csv`, which adds:
     - `already_pronounceable` (`yes`/`no` with respect to Polish inventory P)
     - `unlocked_by` (semicolon-separated list of English phonemes in E \ P that would unlock the word).

3. **Filter for “A1 + Polish-pronounceable”**
   - Script: `lexicon/filter_oxford_by_level.py`
   - Command (example):
     - `python3 -m lexicon.filter_oxford_by_level --unlocks lexicon/lexicon_oxford3000_unlocks.csv --out lexicon/oxford3000_A1_polish_pronounceable.csv --level A1`
   - Output: `lexicon/oxford3000_A1_polish_pronounceable.csv`, containing only rows where:
     - `level == "A1"`
     - `already_pronounceable == "yes"`
   - At the moment, this file is effectively empty because `data/oxford_levels.csv` only contains a header. Once CEFR levels are populated, it will become the core list of **A1 Oxford words that are fully pronounceable with the Polish inventory**.

### How this feeds ClearPronounce curricula

- The A1 + pronounceable subset is the natural candidate pool for:
  - Unit Zero / early vocabulary, where no new phonemes beyond the Polish inventory are required.
  - Early reading and listening materials where pronunciation burden is intentionally low.
- Words that are A1 but **not** in this subset (i.e. `already_pronounceable == "no"`) can be grouped by their `unlocked_by` phonemes to form:
  - “New sound” units (e.g. words unlocked by `/θ/`, `/ð/`, `/ə/`).
  - Phoneme-specific practice lists that build on the safe A1 base.

Once `oxford_levels.csv` is filled with real level data, re-running the three steps above will regenerate all downstream files and keep the curriculum-aligned word lists in sync.

