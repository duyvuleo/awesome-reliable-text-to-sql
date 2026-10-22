#!/usr/bin/env python3
"""Build the original SVG identity assets using only the Python standard library."""

from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PALETTES = {
    "light": {"bg": "#f6f8fc", "ink": "#172b45", "muted": "#50627a", "line": "#c8d5e3", "panel": "#ffffff"},
    "dark": {"bg": "#101c2f", "ink": "#f1f5fc", "muted": "#b8c8db", "line": "#3c506c", "panel": "#192a42"},
}


def graphic(social=False, theme="light"):
    palette = PALETTES[theme]
    width, height = 1280, 640 if social else 360
    title_size = 78 if social else 68
    y_title = 244 if social else 156
    y_second = 336 if social else 232
    y_topics = 414 if social else 286
    y_footer = 568 if social else 330
    graphic_offset = 112 if social else 0
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Awesome Reliable Text-to-SQL</title>',
        '<desc id="desc">An annotated research collection about ambiguity, clarification, and unanswerability. A question branches to clarify, answer, or abstain.</desc>',
        f'<rect width="1280" height="{height}" rx="24" fill="{palette["bg"]}"/>',
        '<rect x="72" y="54" width="34" height="5" rx="2.5" fill="#37b4a0"/>',
    ]

    def text(x, y, value, size, color=None, weight=400, anchor="start", spacing=None):
        tracking = f' letter-spacing="{spacing}"' if spacing is not None else ""
        elements.append(f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color or palette["ink"]}"{tracking}>{escape(value)}</text>')

    def line(points):
        elements.append(f'<path d="{points}" stroke="{palette["line"]}" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')

    text(72, 90, "AWESOME RESEARCH COLLECTION", 15, palette["muted"], 600, spacing=2.2)
    text(68, y_title, "Reliable", title_size, weight=700)
    text(68, y_second, "Text-to-SQL", title_size, weight=700)
    text(72, y_topics, "Ambiguity · Clarification · Unanswerability", 21, palette["muted"])
    text(72, y_footer, "duyvuleo / awesome-reliable-text-to-sql", 15, palette["muted"])

    top = 62 + graphic_offset
    elements.append(f'<rect x="834" y="{top}" width="310" height="58" rx="14" fill="{palette["panel"]}" stroke="{palette["line"]}"/>')
    text(989, top + 36, "User question", 21, weight=600, anchor="middle")
    line(f'M 989 {top + 58} V {top + 92} M 851 {top + 118} V {top + 92} H 1127 V {top + 118} M 989 {top + 92} V {top + 118}')
    cards = [(795, "Clarify", "#168571" if theme == "light" else "#74d7c4"),
             (933, "Answer", "#315da7" if theme == "light" else "#9bbcf6"),
             (1071, "Abstain", "#93601d" if theme == "light" else "#edc179")]
    for x, label, color in cards:
        elements.append(f'<rect x="{x}" y="{top + 118}" width="112" height="76" rx="14" fill="{palette["panel"]}" stroke="{palette["line"]}"/>')
        elements.append(f'<circle cx="{x + 56}" cy="{top + 140}" r="4" fill="{color}"/>')
        text(x + 56, top + 172, label, 19, color, 600, anchor="middle")
    text(989, top + 241, "Papers · Systems · Datasets", 18, palette["muted"], anchor="middle")
    elements.append("</svg>")
    return "\n".join(elements) + "\n"


def main():
    folder = ROOT / "assets"
    folder.mkdir(exist_ok=True)
    for theme in PALETTES:
        (folder / f"banner-{theme}.svg").write_text(graphic(theme=theme), encoding="utf-8")
    (folder / "social-preview.svg").write_text(graphic(social=True, theme="dark"), encoding="utf-8")
    print("Built light/dark SVG banners and the social-preview SVG.")


if __name__ == "__main__":
    main()
