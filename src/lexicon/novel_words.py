"""Deterministic novel-word generator for the novel-lexical condition.

Forms are phonotactically legal CVC or CVCC stems with regular -s / -ed
inflection. A stem is rejected if it, or those inflected forms, collide with
the English wordlist, the extra blocklist (real words and brands missing from
the frequency list), or stems already issued in this generation.
"""

from __future__ import annotations

import random
from pathlib import Path

WORDLIST_PATH = Path(__file__).resolve().parent / "english_wordlist.txt"
SUPPLEMENT_PATH = Path(__file__).resolve().parent / "supplemental_blocklist.txt"

# Legal single-vowel onsets and codas. Codas exclude s/x/z so pluralization
# stays regular -s rather than -es. Stems never end in e, so past is always -ed.
ONSETS = (
    "b", "bl", "br", "d", "dr", "f", "fl", "fr", "g", "gl", "gr",
    "k", "kl", "kr", "l", "m", "n", "p", "pl", "pr", "r", "s",
    "sk", "sl", "sm", "sn", "sp", "st", "sw", "t", "tr", "v", "w", "z",
)
VOWELS = ("a", "e", "i", "o", "u")
CVC_CODAS = ("b", "d", "f", "g", "k", "l", "m", "n", "p", "t")
CVCC_CODAS = ("mp", "nd", "nk", "nt", "lp", "lt", "rk", "rp", "sk", "sp", "st")

# Real words and brands the frequency list misses. New stems are also blocked
# against supplemental_blocklist.txt. Existing Berko nonce "wug" is not a real
# English word and is not blocked; it stays as the classic novel-word stem.
BLOCKLIST = {
    "yomp",
    "teck",
    "tech",
    "snorg",
    "gag",
    "google",
    "nike",
    "apple",
    "amazon",
    "tesla",
    "xbox",
    "skype",
    "uber",
    "lyft",
    "ikea",
    "lego",
    "sony",
    "nokia",
    "volvo",
}


def load_wordlist(path: Path | None = None) -> set[str]:
    source = path or WORDLIST_PATH
    words = set(BLOCKLIST)
    for path in (source, SUPPLEMENT_PATH):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            token = line.strip().lower()
            if token and not token.startswith("#"):
                words.add(token)
    return words


def is_phonotactically_legal(stem: str) -> bool:
    text = stem.lower()
    for onset in sorted(ONSETS, key=len, reverse=True):
        if not text.startswith(onset):
            continue
        rest = text[len(onset) :]
        if len(rest) < 2 or rest[0] not in VOWELS:
            continue
        coda = rest[1:]
        if coda in CVC_CODAS or coda in CVCC_CODAS:
            return True
    return False


def inflected_forms(stem: str) -> tuple[str, str]:
    return f"{stem}s", f"{stem}ed"


def collides(stem: str, wordlist: set[str]) -> bool:
    plural, past = inflected_forms(stem)
    return any(form in wordlist for form in (stem, plural, past))


def generate_novel_stems(
    n: int,
    *,
    seed: int = 0,
    wordlist: set[str] | None = None,
    blocked: set[str] | None = None,
) -> list[str]:
    """Return ``n`` distinct legal stems, deterministically for a given seed."""
    banned = set(wordlist if wordlist is not None else load_wordlist())
    banned.update(blocked or ())
    rng = random.Random(seed)
    issued: list[str] = []
    seen = set(banned)
    # Bound the search so a tiny allow-set fails loudly instead of spinning.
    attempts = 0
    limit = max(1000, n * 500)
    while len(issued) < n:
        attempts += 1
        if attempts > limit:
            raise RuntimeError(f"Could not generate {n} novel stems after {limit} attempts")
        onset = rng.choice(ONSETS)
        vowel = rng.choice(VOWELS)
        coda = rng.choice(CVCC_CODAS if rng.random() < 0.45 else CVC_CODAS)
        stem = f"{onset}{vowel}{coda}"
        if stem in seen or not is_phonotactically_legal(stem) or collides(stem, banned):
            continue
        seen.add(stem)
        seen.add(f"{stem}s")
        seen.add(f"{stem}ed")
        issued.append(stem)
    return issued
