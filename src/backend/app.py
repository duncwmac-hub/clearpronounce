from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.responses import FileResponse

from src.core.frequency_scoring import compute_scores, load_global_freq
from src.core.lexicon_service import LexEntry, load_lexicon
from src.core.text_processing import vocab_from_text, normalise_token, DEFAULT_STOPWORDS
from lexicon.ingest_cmudict import ARPABET_TO_IPA, strip_stress, load_cmudict
from lexicon.respelling_rules import load_respelling_rules


app = FastAPI(title="ClearPronounce API", version="0.1.0")

# Allow cross-origin requests so the file:// frontend can call the API in development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory resources; populated either via init_resources (tests)
# or on startup from CSV files (app runtime).
GLOBAL_FREQ: Dict[str, Tuple[int, float]] = {}
LEXICON: Dict[str, LexEntry] = {}
RESPELLING_OVERRIDES: Dict[str, str] = {}
IPA_OVERRIDES: Dict[str, str] = {}
RESP_RULES = load_respelling_rules()
# All CMUdict pronunciation variants per lowercased word.
CMU_VARIANTS: Dict[str, List[str]] = {}

try:  # POS tagging is a must-have but should fail soft if model unavailable.
    import spacy

    NLP = spacy.load(os.environ.get("CP_SPACY_MODEL", "en_core_web_sm"))
except Exception:  # pragma: no cover - spaCy/model may not be present in some environments.
    NLP = None


def _generate_stressed_respelling(ipa: str, cmu_pron: str) -> str:
    """Generate a respelling string with the primary-stress chunk bolded and capitalised.

    This recomputes the respelling from IPA + rules (ignoring any manual overrides),
    but keeps the plain respelling field unchanged for CSV/export.
    """
    ipa = (ipa or "").strip()
    cmu_pron = (cmu_pron or "").strip()
    if not ipa or not cmu_pron:
        return ""

    phones_arpabet = cmu_pron.split()

    # Find primary-stress phone index in ARPABET.
    primary_index = -1
    for idx, p in enumerate(phones_arpabet):
        if p and p[-1] == "1":
            primary_index = idx
            break
    if primary_index < 0:
        return ""

    # Identify syllable nuclei (vowels) by ARPABET base symbol.
    vowel_bases = {
        "IY",
        "IH",
        "EY",
        "EH",
        "AE",
        "AA",
        "AO",
        "UH",
        "UW",
        "AH",
        "ER",
        "AY",
        "OY",
        "AW",
        "OW",
    }
    vowel_indices: list[int] = []
    for idx, p in enumerate(phones_arpabet):
        base = strip_stress(p)
        if base in vowel_bases:
            vowel_indices.append(idx)

    if not vowel_indices:
        return ""

    # Map the primary-stress phone index to a syllable index.
    primary_syllable_idx = -1
    for s_idx, v_idx in enumerate(vowel_indices):
        if v_idx == primary_index:
            primary_syllable_idx = s_idx
            break
    if primary_syllable_idx < 0:
        return ""

    syllable_count = len(vowel_indices)

    # Decide whether to highlight stress at all.
    # - Do not highlight in monosyllables.
    # - Do not highlight when stress is on the penultimate syllable.
    do_highlight = True
    if syllable_count == 1:
        do_highlight = False
    elif primary_syllable_idx == syllable_count - 2:
        do_highlight = False

    # Determine stressed syllable span in phone indices (inclusive).
    stress_span_start = vowel_indices[primary_syllable_idx]
    if primary_syllable_idx + 1 < syllable_count:
        stress_span_end = vowel_indices[primary_syllable_idx + 1] - 1
    else:
        stress_span_end = len(phones_arpabet) - 1

    ipa_phones = [p for p in ipa.split() if p]
    # Map ARPABET -> IPA bases to align indices if needed.
    ipa_from_arpabet = []
    for p in phones_arpabet:
        base = strip_stress(p)
        ipa_equiv = ARPABET_TO_IPA.get(base)
        if ipa_equiv is None:
            # Fallback: keep base so lengths still align as best we can.
            ipa_equiv = base
        ipa_from_arpabet.append(ipa_equiv)

    if len(ipa_from_arpabet) != len(ipa_phones):
        # If we can't safely align, bail out rather than mis-mark stress.
        return ""

    pieces: list[str] = []
    for idx, phone in enumerate(ipa_phones):
        rule = RESP_RULES.get(phone)
        chunk = rule.default_letters if rule is not None else phone
        # For careful / teacher-facing respelling, treat a word-initial
        # pre-stress schwa as a clearer full vowel for learners.
        if idx == 0 and idx < primary_index and phone == "ə":
            chunk = "a"
        if do_highlight and stress_span_start <= idx <= stress_span_end:
            chunk = f"<strong>{chunk.upper()}</strong>"
        pieces.append(chunk)
    return "".join(pieces)


def init_resources(
    global_freq: Dict[str, Tuple[int, float]],
    lexicon: Dict[str, LexEntry],
) -> None:
    """Initialise global frequency and lexicon mappings for the app.

    This is mainly used in tests; a real deployment can load from CSVs
    in a startup event.
    """
    global GLOBAL_FREQ, LEXICON, CMU_VARIANTS
    GLOBAL_FREQ = dict(global_freq)
    LEXICON = dict(lexicon)


class AnalyzeRequest(BaseModel):
    text: str = Field(..., description="English exercise text to analyse.")


class WordResult(BaseModel):
    word: str
    localCount: int
    globalRank: Optional[int] = None
    globalFreqPerMillion: Optional[float] = None
    score: float
    ipa: str = ""
    respelling: str = ""
    respellingStressed: str = ""
    alreadyPronounceable: Optional[bool] = None
    unlockedBy: str = ""


class AnalyzeResponse(BaseModel):
    words: List[WordResult]


class VariantClick(BaseModel):
    variant: str


def _parse_phoneme_set(s: str) -> set[str]:
    """Parse a phoneme_set field like "{b, d, n, æ, ʌ}" into a set."""
    s = (s or "").strip()
    if s.startswith("{") and s.endswith("}"):
        s = s[1:-1]
    if not s:
        return set()
    return {item.strip() for item in s.split(",") if item.strip()}


def _load_polish_inventory(path: Path) -> set[str]:
    """Load Polish phoneme inventory from markdown (first /.../ line)."""
    if not path.exists():
        return set()
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("/") and line.endswith("/"):
                inner = line[1:-1]
                return {p.strip() for p in inner.split(",") if p.strip()}
    return set()


@app.on_event("startup")
def load_resources_from_disk() -> None:
    """Load global frequency and lexicon from CSVs on startup.

    Paths are taken from environment variables if present, otherwise
    sensible defaults inside the repository are used.
    """
    global GLOBAL_FREQ, LEXICON

    # base_dir should be the project root (one level above src/)
    base_dir = Path(__file__).resolve().parents[2]
    data_dir = base_dir / "data"
    lexicon_dir = base_dir / "lexicon"
    rules_dir = base_dir / "rules"

    freq_path = Path(
        os.environ.get(
            "CP_GLOBAL_FREQ_PATH",
            str(data_dir / "global_freq_template.csv"),
        )
    )
    lexicon_path = Path(
        os.environ.get(
            "CP_LEXICON_PATH",
            str(lexicon_dir / "lexicon_oxford3000.csv"),
        )
    )
    polish_inventory_path = Path(
        os.environ.get(
            "CP_POLISH_INVENTORY_PATH",
            str(rules_dir / "phonemes_polish.md"),
        )
    )
    overrides_path = Path(
        os.environ.get(
            "CP_RESPEL_OVERRIDES_PATH",
            str(lexicon_dir / "respelling_overrides.csv"),
        )
    )

    try:
        if freq_path.exists():
            GLOBAL_FREQ = load_global_freq(freq_path)
        else:
            GLOBAL_FREQ = {}
        if lexicon_path.exists():
            LEXICON = load_lexicon(lexicon_path)
        else:
            LEXICON = {}

        # Optional respelling and IPA overrides (e.g. the → ð ə / ðə for schwa).
        global RESPELLING_OVERRIDES, IPA_OVERRIDES
        RESPELLING_OVERRIDES = {}
        IPA_OVERRIDES = {}
        if overrides_path.exists():
            with overrides_path.open(encoding="utf-8", newline="") as f:
                for row in csv.DictReader(f):
                    w = (row.get("word") or "").strip().lower()
                    r = (row.get("respelling") or "").strip()
                    ipa_override = (row.get("ipa") or "").strip()
                    if w and r:
                        RESPELLING_OVERRIDES[w] = r
                    if w and ipa_override:
                        IPA_OVERRIDES[w] = ipa_override

        # Load CMUdict variants so we can choose pronunciations per token later.
        cmudict_path = Path(
            os.environ.get(
                "CP_CMUDICT_PATH",
                str(data_dir / "CMUdict" / "cmudict.dict"),
            )
        )
        if cmudict_path.exists():
            CMU_VARIANTS = load_cmudict(cmudict_path)
        else:
            CMU_VARIANTS = {}

        # Enrich lexicon entries with pronounceability info vs Polish inventory.
        polish_inventory = _load_polish_inventory(polish_inventory_path)
        if polish_inventory:
            for entry in LEXICON.values():
                phones = _parse_phoneme_set(entry.phoneme_set)
                if not phones:
                    continue
                needs_new = sorted(phones - polish_inventory)
                if not needs_new:
                    entry.already_pronounceable = True
                    entry.unlocked_by = ""
                else:
                    entry.already_pronounceable = False
                    entry.unlocked_by = ";".join(needs_new)
    except Exception:
        # Fail soft: keep empty mappings so the API still works,
        # just without global ranking or pronunciation data.
        GLOBAL_FREQ = GLOBAL_FREQ or {}
        LEXICON = LEXICON or {}


@app.post("/analyze-text", response_model=AnalyzeResponse)
def analyze_text(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Analyse raw text and return a ranked vocab list with pronunciation data."""
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text must not be empty.")
    if len(text) > 10_000:
        raise HTTPException(status_code=413, detail="Text is too long.")

    # Build lemma counts (as before).
    counts = vocab_from_text(text)
    scored = compute_scores(counts, GLOBAL_FREQ or None)

    # Very light POS awareness: map lemmas to dominant POS tags using spaCy,
    # while preserving existing vocab_from_text behaviour.
    lemma_pos: Dict[str, Dict[str, int]] = {}
    if NLP is not None:
        stop = set(DEFAULT_STOPWORDS)
        doc = NLP(text)
        for token in doc:
            if not token.is_alpha:
                continue
            lemma = normalise_token(token.text)
            if len(lemma) < 2 or lemma in stop:
                continue
            pos_tag = token.pos_ or token.tag_ or ""
            if not pos_tag:
                continue
            lemma_pos.setdefault(lemma, {})
            lemma_pos[lemma][pos_tag] = lemma_pos[lemma].get(pos_tag, 0) + 1

    results: List[WordResult] = []
    for word, local_count, rank, freq_pm, score in scored:
        entry = LEXICON.get(word)
        ipa = IPA_OVERRIDES.get(word.lower()) or (entry.ipa if entry else "")
        resp = RESPELLING_OVERRIDES.get(word.lower()) or (entry.respelling if entry else "")
        resp_stressed = (
            _generate_stressed_respelling(ipa, entry.cmu_pron)
            if entry and entry.cmu_pron
            else ""
        )
        already = entry.already_pronounceable if entry else None
        unlocked = entry.unlocked_by if entry else ""

        results.append(
            WordResult(
                word=word,
                localCount=local_count,
                globalRank=rank,
                globalFreqPerMillion=freq_pm,
                score=score,
                ipa=ipa,
                respelling=resp,
                respellingStressed=resp_stressed,
                alreadyPronounceable=already,
                unlockedBy=unlocked,
            )
        )

    return AnalyzeResponse(words=results)


@app.post("/track-variant")
def track_variant(payload: VariantClick) -> dict:
    """Very lightweight tracking endpoint for landing-page promise tests.

    For now we just log to stdout; Render will capture this in its logs.
    """
    variant = (payload.variant or "").strip() or "unknown"
    print(f"[variant_click] variant={variant}")  # noqa: T201
    return {"ok": True}


# Serve frontend at same origin when deployed (one host for clearpronounce.com).
_base_dir = Path(__file__).resolve().parents[2]
_frontend_dir = _base_dir / "src" / "frontend"


@app.get("/")
def _serve_app() -> FileResponse:
    """Serve the single-page app so /docs and /analyze-text remain available."""
    index = _frontend_dir / "index.html"
    if not index.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(index)

