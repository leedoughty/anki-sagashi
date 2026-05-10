import pytest

from anki_sagashi.input import detect_and_read_input


def test_text_flag():
    result = detect_and_read_input(source=None, text="テスト文章")
    assert result == "テスト文章"


def test_file_input(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("ファイルから読む", encoding="utf-8")
    result = detect_and_read_input(source=str(f), text=None)
    assert result == "ファイルから読む"


def test_no_input_raises():
    with pytest.raises(SystemExit):
        detect_and_read_input(source=None, text=None)


def test_nonexistent_file_raises():
    with pytest.raises(SystemExit):
        detect_and_read_input(source="/nonexistent/path.txt", text=None)
