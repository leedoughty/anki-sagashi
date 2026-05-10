import pytest

from anki_sagashi.anki import (
    CardStatus,
    WordResult,
    check_vocabulary,
    classify_word,
    find_note_count,
)


def test_classify_unknown():
    assert classify_word(0) == CardStatus.UNKNOWN


def test_classify_thin():
    assert classify_word(1) == CardStatus.THIN


def test_classify_known():
    assert classify_word(2) == CardStatus.KNOWN
    assert classify_word(5) == CardStatus.KNOWN


def test_find_note_count(httpx_mock):
    httpx_mock.add_response(json={"result": [1001, 1002, 1003], "error": None})
    assert find_note_count("猫") == 3


def test_find_note_count_empty(httpx_mock):
    httpx_mock.add_response(json={"result": [], "error": None})
    assert find_note_count("齟齬") == 0


def test_check_vocabulary(httpx_mock):
    httpx_mock.add_response(json={"result": [], "error": None})
    httpx_mock.add_response(json={"result": [101], "error": None})
    httpx_mock.add_response(json={"result": [201, 202, 203], "error": None})

    lemmas = {
        "未知": ("ミチ", "名詞", 3),
        "薄い": ("ウスイ", "形容詞", 2),
        "既知": ("キチ", "名詞", 1),
    }

    results = check_vocabulary(lemmas)

    by_lemma = {r.lemma: r for r in results}
    assert by_lemma["未知"].status == CardStatus.UNKNOWN
    assert by_lemma["薄い"].status == CardStatus.THIN
    assert by_lemma["既知"].status == CardStatus.KNOWN

    # sorted by frequency descending
    assert results[0].lemma == "未知"
    assert results[1].lemma == "薄い"
    assert results[2].lemma == "既知"


def test_check_vocabulary_connection_error(httpx_mock):
    import httpx as httpx_lib

    httpx_mock.add_exception(httpx_lib.ConnectError("Connection refused"))

    lemmas = {"テスト": ("テスト", "名詞", 1)}

    with pytest.raises(SystemExit, match="cannot connect to AnkiConnect"):
        check_vocabulary(lemmas)
