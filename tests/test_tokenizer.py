from anki_sagashi.tokenizer import tokenize, Token
from anki_sagashi.filters import filter_tokens


def test_tokenize_keeps_content_words():
    result = tokenize("今日は天気がいいですね")
    lemmas = [t.lemma for t in result.tokens]
    assert "天気" in lemmas
    assert "良い" in lemmas or "いい" in lemmas


def test_tokenize_drops_particles():
    result = tokenize("猫が魚を食べた")
    pos_types = {t.pos for t in result.tokens}
    assert "助詞" not in pos_types
    assert "助動詞" not in pos_types


def test_tokenize_lemmatizes():
    result = tokenize("走っている猫を見た")
    lemmas = [t.lemma for t in result.tokens]
    assert "走る" in lemmas
    assert "猫" in lemmas


def test_frequency_count():
    result = tokenize("猫が猫を見た。猫は可愛い。")
    assert result.frequency["猫"] == 3


def test_filter_stopwords():
    result = tokenize("彼は大きい犬を持つ")
    filtered = filter_tokens(result)
    lemmas = [t.lemma for t in filtered.tokens]
    assert "犬" in lemmas
    assert "持つ" not in lemmas


def test_filter_jlpt():
    result = tokenize("天気が良い")
    filtered = filter_tokens(result, min_jlpt="N4")
    lemmas = [t.lemma for t in filtered.tokens]
    # 天気 is N5 (level 5 >= rank 4), should be filtered
    assert "天気" not in lemmas


def test_filter_skip_top():
    result = tokenize("猫が猫と犬と犬と鳥を見た")
    filtered = filter_tokens(result, skip_top=1)
    lemmas = [t.lemma for t in filtered.tokens]
    # 猫 appears most (2x), should be skipped
    assert "猫" not in lemmas
    assert "犬" in lemmas
