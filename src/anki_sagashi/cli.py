from typing import Annotated, Optional

import typer

from anki_sagashi.filters import filter_tokens
from anki_sagashi.input import detect_and_read_input
from anki_sagashi.tokenizer import tokenize

app = typer.Typer(help="Find vocabulary gaps in Japanese text against your Anki deck.")


@app.command()
def scan(
    source: Annotated[
        Optional[str],
        typer.Argument(help="URL, file path, or '-' for stdin"),
    ] = None,
    text: Annotated[
        Optional[str],
        typer.Option("--text", "-t", help="Pass text directly"),
    ] = None,
    min_jlpt: Annotated[
        Optional[str],
        typer.Option("--min-jlpt", help="Skip vocab below this JLPT level (e.g. N3)"),
    ] = None,
    skip_top: Annotated[
        int,
        typer.Option("--skip-top", help="Skip the N most frequent words"),
    ] = 0,
    include_thin: Annotated[
        bool,
        typer.Option("--include-thin", help="Include words with only 1 context in Anki"),
    ] = False,
    output: Annotated[
        Optional[str],
        typer.Option("--output", "-o", help="Output format: table (default) or json"),
    ] = None,
    export: Annotated[
        bool,
        typer.Option("--export", help="Export for anki-tango consumption"),
    ] = False,
) -> None:
    """Scan Japanese text and find vocabulary gaps against your Anki deck."""
    from anki_sagashi.anki import check_vocabulary
    from anki_sagashi.report import render_export, render_json, render_table
    from anki_sagashi.tokenizer import extract_sentences

    raw_text = detect_and_read_input(source=source, text=text)
    result = tokenize(raw_text)
    filtered = filter_tokens(result, min_jlpt=min_jlpt, skip_top=skip_top)

    lemmas: dict[str, tuple[str, str, int]] = {}
    for lemma, count in filtered.frequency.most_common():
        token = next(t for t in filtered.tokens if t.lemma == lemma)
        lemmas[lemma] = (token.reading, token.pos, count)

    results = check_vocabulary(lemmas)

    if export:
        sentences = extract_sentences(raw_text)
        render_export(results, sentences, include_thin)
    elif output == "json":
        render_json(results, include_thin)
    else:
        render_table(results, include_thin)
