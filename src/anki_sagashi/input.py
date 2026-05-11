import sys
from pathlib import Path

import httpx
from bs4 import BeautifulSoup


def detect_and_read_input(source: str | None, text: str | None) -> str:
    if text is not None:
        return text

    if source is None:
        raise SystemExit("Error: provide a URL, file path, '-' for stdin, or --text")

    if source == "-":
        return sys.stdin.read()

    if source.startswith(("http://", "https://")):
        return fetch_url(source)

    path = Path(source)
    if path.is_file():
        return path.read_text(encoding="utf-8")

    raise SystemExit(f"Error: '{source}' is not a URL, existing file, or '-'")


def fetch_url(url: str) -> str:
    try:
        response = httpx.get(url, follow_redirects=True, timeout=30)
        response.raise_for_status()
    except httpx.ConnectError:
        raise SystemExit(f"Error: could not connect to '{url}'")
    except httpx.TimeoutException:
        raise SystemExit(f"Error: request timed out for '{url}'")
    except httpx.HTTPStatusError as e:
        raise SystemExit(f"Error: HTTP {e.response.status_code} for '{url}'")

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    if not text:
        raise SystemExit(f"Error: no text content extracted from '{url}'")
    return text
