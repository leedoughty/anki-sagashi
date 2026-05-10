# anki-sagashi

A CLI tool that mines Japanese text for vocabulary gaps against your Anki deck.

Feed it an article, get back a list of words you don't have cards for — then pipe those into [anki-tango](https://github.com/leedoughty/anki-tango) for automatic card generation.

## Requirements

- Python 3.11+
- [Anki](https://apps.ankiweb.net/) with [AnkiConnect](https://ankiweb.net/shared/info/2055492159) installed and running
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

```bash
uv tool install .
```

Or for development:

```bash
uv sync
uv run anki-sagashi --help
```

## Usage

```bash
# Scan a URL (fetches and extracts article text)
anki-sagashi scan https://www3.nhk.or.jp/news/easy/...

# Scan a local file
anki-sagashi scan article.txt

# Pass text directly
anki-sagashi scan --text "今日の記事の内容をここに貼り付ける"

# Pipe from clipboard
pbpaste | anki-sagashi scan -
```

### Options

```
--min-jlpt N2       Skip vocab at or below this JLPT level
--skip-top 500      Skip the N most frequent words in the source
--include-thin      Show words with only 1 context in Anki
--output json       Output as JSON instead of table
--export            Export for anki-tango consumption
```

### Output

Default output is a Rich table:

```
                        Vocabulary Gaps
┏━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━┳━━━━━━┳━━━━━━┳━━━━━━━┓
┃ Status  ┃ Word   ┃ Reading  ┃ POS  ┃ Freq ┃ JLPT ┃ Notes ┃
┡━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━╇━━━━━━╇━━━━━━╇━━━━━━━┩
│ unknown │ 齟齬   │ ソゴ     │ 名詞 │    1 │ N2   │     0 │
│ unknown │ 斡旋   │ アッセン │ 名詞 │    1 │ N1   │     0 │
└─────────┴────────┴──────────┴──────┴──────┴──────┴───────┘
```

### Pipeline with anki-tango

```bash
anki-sagashi scan https://example.com/article --export | anki-tango create
```

The `--export` flag outputs JSON with source sentences for context-rich card generation:

```json
[
  {
    "word": "齟齬",
    "reading": "ソゴ",
    "sentence": "齟齬が生じた",
    "jlpt": "N2"
  },
  {
    "word": "斡旋",
    "reading": "アッセン",
    "sentence": "斡旋を試みた",
    "jlpt": "N1"
  }
]
```

## Configuration

Custom stop words can be added in `~/.config/anki-sagashi/config.toml`:

```toml
[stopwords]
extra = ["word1", "word2", "word3"]
```

## How it works

1. Accept input as URL, file, stdin, or raw text
2. Tokenize Japanese with MeCab (via fugashi)
3. Filter by part of speech — keep nouns, verbs, adjectives, adverbs
4. Lemmatize to dictionary form
5. Apply stop list, JLPT floor, and frequency filters
6. Query AnkiConnect for each remaining word
7. Classify: **unknown** (no card), **thin** (1 context), **known** (2+ contexts)
8. Output ranked report
