import json
from importlib.resources import files
from collections import Counter

from anki_sagashi.tokenizer import Token, TokenizeResult


def _load_json(filename: str) -> list | dict:
    data_dir = files("anki_sagashi").joinpath("data", filename)
    return json.loads(data_dir.read_text(encoding="utf-8"))


_stopwords: set[str] | None = None
_jlpt: dict[str, int] | None = None


def get_stopwords() -> set[str]:
    global _stopwords
    if _stopwords is None:
        _stopwords = set(_load_json("stopwords.json"))
    return _stopwords


def get_jlpt_data() -> dict[str, int]:
    global _jlpt
    if _jlpt is None:
        _jlpt = _load_json("jlpt.json")
    return _jlpt


def jlpt_level(word: str) -> int | None:
    data = get_jlpt_data()
    return data.get(word)


JLPT_RANK = {"N5": 5, "N4": 4, "N3": 3, "N2": 2, "N1": 1}


def filter_tokens(
    result: TokenizeResult,
    min_jlpt: str | None = None,
    skip_top: int = 0,
) -> TokenizeResult:
    stopwords = get_stopwords()
    jlpt_data = get_jlpt_data()

    min_jlpt_rank = JLPT_RANK.get(min_jlpt, 0) if min_jlpt else 0

    filtered: list[Token] = []
    seen_lemmas: set[str] = set()

    for token in result.tokens:
        if token.lemma in stopwords:
            continue

        if min_jlpt_rank:
            level = jlpt_data.get(token.lemma)
            if level is not None and level >= min_jlpt_rank:
                continue

        filtered.append(token)

    if skip_top > 0:
        freq = Counter(t.lemma for t in filtered)
        top_words = {word for word, _ in freq.most_common(skip_top)}
        filtered = [t for t in filtered if t.lemma not in top_words]

    return TokenizeResult(tokens=filtered)
