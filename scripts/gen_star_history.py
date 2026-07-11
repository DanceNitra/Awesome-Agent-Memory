#!/usr/bin/env python3
"""Render the repo's star-history chart as self-hosted SVGs.

Fetches stargazer timestamps from the GitHub API and writes
assets/star-history.svg (light) and assets/star-history-dark.svg,
referenced from README.md via a <picture> element. Output is
deterministic for a given set of stargazers, so the weekly CI run
only commits when the star count actually changed.

Usage: GITHUB_TOKEN=... python3 scripts/gen_star_history.py [owner/repo]
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

REPO = sys.argv[1] if len(sys.argv) > 1 else "TeleAI-UAGI/Awesome-Agent-Memory"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")

WIDTH, HEIGHT = 800, 420
PAD_L, PAD_R, PAD_T, PAD_B = 60, 76, 64, 52
MAX_POINTS = 150

THEMES = {
    "light": {
        "file": "star-history.svg",
        "surface": "#fcfcfb",
        "border": "rgba(11,11,11,0.10)",
        "ink": "#0b0b0b",
        "muted": "#898781",
        "grid": "#e1e0d9",
        "baseline": "#c3c2b7",
        "series": "#2a78d6",
    },
    "dark": {
        "file": "star-history-dark.svg",
        "surface": "#1a1a19",
        "border": "rgba(255,255,255,0.10)",
        "ink": "#ffffff",
        "muted": "#898781",
        "grid": "#2c2c2a",
        "baseline": "#383835",
        "series": "#3987e5",
    },
}


def fetch_star_dates(repo):
    token = os.environ.get("GITHUB_TOKEN", "")
    dates, page = [], 1
    while True:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/stargazers?per_page=100&page={page}",
            headers={
                "Accept": "application/vnd.github.star+json",
                "X-GitHub-Api-Version": "2022-11-28",
                **({"Authorization": f"Bearer {token}"} if token else {}),
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            batch = json.load(resp)
        dates += [
            datetime.fromisoformat(s["starred_at"].replace("Z", "+00:00"))
            for s in batch
        ]
        if len(batch) < 100:
            return sorted(dates)
        page += 1


def nice_step(maximum, target_ticks=6):
    for step in [s * 10**e for e in range(6) for s in (1, 2, 5)]:
        if maximum / step <= target_ticks:
            return step
    return maximum


def month_ticks(start, end, max_ticks=6):
    months = []
    y, m = start.year, start.month + 1
    if m > 12:
        y, m = y + 1, 1
    while datetime(y, m, 1, tzinfo=timezone.utc) <= end:
        months.append(datetime(y, m, 1, tzinfo=timezone.utc))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    stride = max(1, -(-len(months) // max_ticks))
    return months[::stride]


def render(dates, theme):
    total = len(dates)
    t0, t1 = dates[0].timestamp(), dates[-1].timestamp()
    span = max(t1 - t0, 1)
    y_step = nice_step(total)
    y_max = max(-(-total // y_step) * y_step, y_step)
    plot_w, plot_h = WIDTH - PAD_L - PAD_R, HEIGHT - PAD_T - PAD_B

    def px(ts):
        return PAD_L + (ts - t0) / span * plot_w

    def py(count):
        return PAD_T + plot_h - count / y_max * plot_h

    points = [(dates[0], 0)] + [(d, i + 1) for i, d in enumerate(dates)]
    if len(points) > MAX_POINTS:
        stride = -(-len(points) // MAX_POINTS)
        points = points[::stride] + [points[-1]]
    coords = [(px(d.timestamp()), py(c)) for d, c in points]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    baseline_y = py(0)

    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
        f'aria-label="Cumulative GitHub stars of {REPO} over time, currently {total}">',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="8" '
        f'fill="{theme["surface"]}" stroke="{theme["border"]}"/>',
        f'<g font-family=\'system-ui, -apple-system, "Segoe UI", sans-serif\'>',
        f'<text x="{PAD_L}" y="32" font-size="15" font-weight="600" '
        f'fill="{theme["ink"]}">{REPO} &#8212; GitHub stars</text>',
    ]

    for tick in range(0, y_max + 1, y_step):
        y = py(tick)
        if tick > 0:
            s.append(
                f'<line x1="{PAD_L}" y1="{y:.1f}" x2="{WIDTH - PAD_R}" y2="{y:.1f}" '
                f'stroke="{theme["grid"]}" stroke-width="1"/>'
            )
        s.append(
            f'<text x="{PAD_L - 10}" y="{y + 4:.1f}" font-size="11" text-anchor="end" '
            f'fill="{theme["muted"]}" font-variant-numeric="tabular-nums">{tick:,}</text>'
        )
    s.append(
        f'<line x1="{PAD_L}" y1="{baseline_y:.1f}" x2="{WIDTH - PAD_R}" '
        f'y2="{baseline_y:.1f}" stroke="{theme["baseline"]}" stroke-width="1"/>'
    )

    for tick in month_ticks(dates[0], dates[-1]):
        x = px(tick.timestamp())
        s.append(
            f'<text x="{x:.1f}" y="{baseline_y + 22:.1f}" font-size="11" '
            f'text-anchor="middle" fill="{theme["muted"]}">{tick.strftime("%b %Y")}</text>'
        )

    end_x, end_y = coords[-1]
    s += [
        f'<polygon points="{line} {end_x:.1f},{baseline_y:.1f} '
        f'{coords[0][0]:.1f},{baseline_y:.1f}" fill="{theme["series"]}" opacity="0.10"/>',
        f'<polyline points="{line}" fill="none" stroke="{theme["series"]}" '
        f'stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>',
        f'<circle cx="{end_x:.1f}" cy="{end_y:.1f}" r="4.5" fill="{theme["series"]}" '
        f'stroke="{theme["surface"]}" stroke-width="2"/>',
        f'<text x="{end_x + 10:.1f}" y="{end_y + 4:.1f}" font-size="13" '
        f'font-weight="600" fill="{theme["ink"]}">{total:,}</text>',
        "</g></svg>",
    ]
    return "\n".join(s) + "\n"


def main():
    dates = fetch_star_dates(REPO)
    if not dates:
        sys.exit(f"{REPO} has no stargazers; nothing to plot")
    os.makedirs(OUT_DIR, exist_ok=True)
    for theme in THEMES.values():
        path = os.path.join(OUT_DIR, theme["file"])
        with open(path, "w", newline="\n") as f:
            f.write(render(dates, theme))
        print(f"wrote {path} ({len(dates)} stars)")


if __name__ == "__main__":
    main()
