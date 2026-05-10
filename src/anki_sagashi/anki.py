from dataclasses import dataclass
from enum import Enum

import httpx


ANKI_CONNECT_URL = "http://localhost:8765"


class CardStatus(Enum):
    UNKNOWN = "unknown"
    THIN = "thin"
    KNOWN = "known"


@dataclass
class WordResult:
    lemma: str
    reading: str
    pos: str
    frequency: int
    status: CardStatus
    note_count: int


def _invoke(action: str, **params) -> dict:
    payload = {"action": action, "version": 6}
    if params:
        payload["params"] = params
    response = httpx.post(ANKI_CONNECT_URL, json=payload, timeout=10)
    response.raise_for_status()
    body = response.json()
    if body.get("error"):
        raise RuntimeError(f"AnkiConnect error: {body['error']}")
    return body["result"]


def find_note_count(word: str) -> int:
    note_ids = _invoke("findNotes", query=f'"{word}"')
    return len(note_ids)


def classify_word(note_count: int) -> CardStatus:
    if note_count == 0:
        return CardStatus.UNKNOWN
    if note_count == 1:
        return CardStatus.THIN
    return CardStatus.KNOWN


def check_vocabulary(lemmas: dict[str, tuple[str, str, int]]) -> list[WordResult]:
    """Check a batch of lemmas against AnkiConnect.

    Args:
        lemmas: mapping of lemma -> (reading, pos, frequency)

    Returns:
        List of WordResult sorted by frequency descending.
    """
    results: list[WordResult] = []

    for lemma, (reading, pos, freq) in lemmas.items():
        try:
            count = find_note_count(lemma)
        except (httpx.ConnectError, httpx.TimeoutException):
            raise SystemExit(
                "Error: cannot connect to AnkiConnect at localhost:8765. "
                "Make sure Anki is running with AnkiConnect installed."
            )
        status = classify_word(count)
        results.append(WordResult(
            lemma=lemma,
            reading=reading,
            pos=pos,
            frequency=freq,
            status=status,
            note_count=count,
        ))

    results.sort(key=lambda r: r.frequency, reverse=True)
    return results
