"""Generate the MAIC Nexus T1 pitch PDF directly from PITCH_DECK.md."""

from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "PITCH_DECK.md"
OUTPUT = ROOT / "pitch_deck.pdf"
COLORS = {
    "background": "#0B1020", "accent": "#36DDB4",
    "heading": "#F5F7FB", "body": "#E5EDF5", "muted": "#A7B7C9"
}
BODY_TOP, LINE_STEP, MAX_LINES = 0.765, 0.043, 15


@dataclass(frozen=True)
class RenderLine:
    text: str
    style: str = "body"


@dataclass(frozen=True)
class Slide:
    number: int
    title: str
    lines: tuple[RenderLine, ...]


def parse_slides(md: str) -> list[Slide]:
    pattern = re.compile(r"^## Slide (\d+)\s*[—–-]\s*(.+)$", re.MULTILINE)
    anchors = list(pattern.finditer(md))
    if not anchors:
        raise ValueError("No numbered pitch slides found.")
    slides = []
    for idx, match in enumerate(anchors):
        end = (
            anchors[idx + 1].start() if idx + 1 < len(anchors)
            else md.find("\n## Harsh-judge quick answers", match.end())
        )
        if end < 0:
            end = len(md)
        number = int(match.group(1))
        if number != idx + 1:
            raise ValueError("Non-consecutive pitch slide numbers.")
        slides.append(
            Slide(number, match.group(2).strip(),
                  tuple(_render_lines(md[match.end():end].strip())))
        )
    return slides


def _plain(s: str) -> str:
    s = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = s.replace("**", "").replace(chr(96), "").replace("*", "")
    return (
        s.replace("≤", "<=").replace("≥", ">=").replace("→", "->")
         .replace("\u00a0", " ").replace("$", r"\$").strip()
    )


def _wrap_line(text: str, style: str) -> Iterable[RenderLine]:
    initial, indent = "", ""
    if style == "bullet":
        m = re.match(r"^(\d+\.\s+)", text)
        if m:
            initial, text = m.group(1), text[m.end():]
        else:
            initial, text = "•  ", re.sub(r"^[-*]\s*", "", text)
        indent = " " * len(initial)
    text = _plain(text)
    if not text:
        return
    for part in textwrap.wrap(
        initial + text,
        width=100 if style == "code" else 90,
        subsequent_indent=indent,
        break_long_words=True,
        break_on_hyphens=False,
    ):
        yield RenderLine(part, style)


def _render_lines(raw: str) -> Iterable[RenderLine]:
    in_code, source_emitted = False, False
    for entry in raw.splitlines():
        line, stripped = entry.rstrip(), entry.strip()
        if stripped.startswith(chr(96) * 3):
            in_code = not in_code
            continue
        if not stripped or stripped == "---":
            yield RenderLine("", "space")
            continue
        if in_code:
            yield RenderLine(line[:105], "code")
            continue
        if stripped.startswith(("http://", "https://", "- http://", "- https://")):
            if not source_emitted:
                yield RenderLine(
                    "Primary references: official SEDA Malaysia ATAP and NEM programme guidance.",
                    "source",
                )
                source_emitted = True
            continue
        if stripped.startswith("#"):
            yield from _wrap_line(stripped.lstrip("#").strip(), "subheading")
        elif re.match(r"^(?:[-*]\s+|\d+\.\s+)", stripped):
            yield from _wrap_line(stripped, "bullet")
        else:
            yield from _wrap_line(stripped, "body")


def _paginate(lines: tuple[RenderLine, ...]) -> list[list[RenderLine]]:
    pages: list[list[RenderLine]] = []
    current: list[RenderLine] = []
    for item in lines:
        if item.style == "space" and (not current or current[-1].style == "space"):
            continue
        if len(current) >= MAX_LINES:
            while current and current[-1].style == "space":
                current.pop()
            pages.append(current)
            current = []
        if item.style == "space" and not current:
            continue
        current.append(item)
    while current and current[-1].style == "space":
        current.pop()
    if current:
        pages.append(current)
    if len(pages) > 1 and len(pages[-1]) < 10:
        combined = pages[-2] + pages[-1]
        midpoint = (len(combined) + 1) // 2
        pages[-2:] = [combined[:midpoint], combined[midpoint:]]
    return pages or [[RenderLine("No slide content supplied.")]]


def _paint(
    pdf: PdfPages, slide: Slide, part: int, total_parts: int,
    content: list[RenderLine], page: int, total_pages: int,
) -> None:
    fig = plt.figure(figsize=(13.333, 7.5), dpi=120,
                     facecolor=COLORS["background"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(plt.Rectangle(
        (0.062, 0.91), 0.875, 0.004,
        color=COLORS["accent"], transform=ax.transAxes
    ))
    ax.text(
        0.07, 0.944, "MAIC NEXUS 2026  /  T1 CLEAN ENERGY",
        fontsize=10.5, color=COLORS["accent"], va="top", weight="bold",
    )
    heading = _plain(slide.title)
    if total_parts > 1:
        heading += f"  (part {part}/{total_parts})"
    ax.text(0.07, 0.872, heading, fontsize=25,
            color=COLORS["heading"], va="top", weight="bold")
    for i, item in enumerate(content):
        ypos = BODY_TOP - i * LINE_STEP
        if ypos < 0.11:
            raise ValueError(f"Overflow on PDF page {page}")
        if item.style == "space":
            continue
        font_size = {
            "subheading": 17, "body": 15.6, "bullet": 15.1,
            "code": 13, "source": 12.5,
        }[item.style]
        color = (
            COLORS["accent"] if item.style == "subheading"
            else COLORS["muted"] if item.style == "source"
            else COLORS["body"]
        )
        ax.text(
            0.088 if item.style == "bullet" else 0.077, ypos,
            item.text, fontsize=font_size, color=color,
            family="DejaVu Sans Mono" if item.style == "code" else "DejaVu Sans",
            weight="bold" if item.style == "subheading" else "normal",
            va="top", ha="left",
        )
    ax.text(
        0.07, 0.056,
        "PRELIMINARY SCREENING  |  SYNTHETIC FIXTURES  |  NOT LEGAL / TNB APPROVAL",
        fontsize=9.3, color=COLORS["muted"], ha="left", va="bottom",
    )
    ax.text(0.94, 0.056, f"{page} / {total_pages}",
            fontsize=10.5, color=COLORS["muted"], ha="right", va="bottom")
    pdf.savefig(fig, dpi=120, facecolor=COLORS["background"])
    plt.close(fig)


def build(source: Path = SOURCE, output: Path = OUTPUT) -> tuple[int, int]:
    slides = parse_slides(source.read_text(encoding="utf-8"))
    sections = [(slide, _paginate(slide.lines)) for slide in slides]
    total_pages = sum(len(parts) for _, parts in sections)
    output.parent.mkdir(parents=True, exist_ok=True)
    page = 0
    with PdfPages(str(output)) as pdf:
        for slide, parts in sections:
            for part_number, lines in enumerate(parts, 1):
                page += 1
                _paint(pdf, slide, part_number, len(parts),
                       lines, page, total_pages)
    if output.stat().st_size < 10000:
        raise RuntimeError("Pitch PDF appears truncated.")
    return len(slides), total_pages


if __name__ == "__main__":
    print("[Pitch PDF] slides / pages:", build())
