import sys
from pathlib import Path
from typing import Annotated, Optional

import typer

from anki_sagashi.input import detect_and_read_input

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
    result = detect_and_read_input(source=source, text=text)
    typer.echo(result)
