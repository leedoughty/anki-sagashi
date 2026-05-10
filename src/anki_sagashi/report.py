import json

from rich.console import Console
from rich.table import Table

from anki_sagashi.anki import CardStatus, WordResult
from anki_sagashi.filters import jlpt_level

JLPT_LABELS = {5: "N5", 4: "N4", 3: "N3", 2: "N2", 1: "N1"}


def render_table(results: list[WordResult], include_thin: bool) -> None:
    console = Console()
    table = Table(title="Vocabulary Gaps")

    table.add_column("Status", style="bold")
    table.add_column("Word")
    table.add_column("Reading")
    table.add_column("POS")
    table.add_column("Freq", justify="right")
    table.add_column("JLPT")
    table.add_column("Notes", justify="right")

    for r in results:
        if r.status == CardStatus.KNOWN:
            continue
        if r.status == CardStatus.THIN and not include_thin:
            continue

        if r.status == CardStatus.UNKNOWN:
            status_text = "[red]unknown[/red]"
        else:
            status_text = "[yellow]thin[/yellow]"

        level = jlpt_level(r.lemma)
        jlpt_text = JLPT_LABELS.get(level, "-") if level else "-"

        table.add_row(
            status_text,
            r.lemma,
            r.reading,
            r.pos,
            str(r.frequency),
            jlpt_text,
            str(r.note_count),
        )

    if table.row_count == 0:
        console.print("[green]No vocabulary gaps found![/green]")
    else:
        console.print(table)


def render_json(results: list[WordResult], include_thin: bool) -> None:
    output = []
    for r in results:
        if r.status == CardStatus.KNOWN:
            continue
        if r.status == CardStatus.THIN and not include_thin:
            continue

        level = jlpt_level(r.lemma)
        output.append({
            "lemma": r.lemma,
            "reading": r.reading,
            "pos": r.pos,
            "frequency": r.frequency,
            "status": r.status.value,
            "note_count": r.note_count,
            "jlpt": JLPT_LABELS.get(level) if level else None,
        })

    print(json.dumps(output, ensure_ascii=False, indent=2))


def render_export(
    results: list[WordResult],
    sentences: dict[str, str],
    include_thin: bool,
) -> None:
    """Export format for anki-tango consumption."""
    output = []
    for r in results:
        if r.status == CardStatus.KNOWN:
            continue
        if r.status == CardStatus.THIN and not include_thin:
            continue

        level = jlpt_level(r.lemma)
        output.append({
            "word": r.lemma,
            "reading": r.reading,
            "sentence": sentences.get(r.lemma, ""),
            "jlpt": JLPT_LABELS.get(level) if level else None,
        })

    print(json.dumps(output, ensure_ascii=False, indent=2))
