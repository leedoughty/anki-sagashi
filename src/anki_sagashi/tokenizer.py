from dataclasses import dataclass, field
from collections import Counter

import fugashi


@dataclass
class Token:
    surface: str
    lemma: str
    pos: str
    reading: str


@dataclass
class TokenizeResult:
    tokens: list[Token]
    frequency: Counter = field(default_factory=Counter)

    def __post_init__(self):
        self.frequency = Counter(t.lemma for t in self.tokens)


KEEP_POS = {"名詞", "動詞", "形容詞", "副詞"}

_tagger: fugashi.Tagger | None = None


def _get_tagger() -> fugashi.Tagger:
    global _tagger
    if _tagger is None:
        _tagger = fugashi.Tagger()
    return _tagger


def tokenize(text: str) -> TokenizeResult:
    tagger = _get_tagger()
    tokens: list[Token] = []

    for word in tagger(text):
        if word.feature.pos1 not in KEEP_POS:
            continue

        lemma = word.feature.lemma or word.surface
        reading = word.feature.kana or word.feature.pron or ""

        tokens.append(Token(
            surface=word.surface,
            lemma=lemma,
            pos=word.feature.pos1,
            reading=reading,
        ))

    return TokenizeResult(tokens=tokens)
