#!/usr/bin/env python3
"""Gerçek GitHub verilerinden günlük güncellenen güvenli bir katkı şehri üret."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import random
import sys
import urllib.error
import urllib.request
from collections import Counter
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "assets" / "contribution-city.svg"

GRAPHQL_QUERY = """
query ProfileDashboard($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, orderBy: {field: UPDATED_AT, direction: DESC}) {
      totalCount
      nodes { primaryLanguage { name color } }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { contributionCount date weekday }
        }
      }
    }
  }
}
"""


def github_data(username: str, token: str) -> dict:
    body = json.dumps({"query": GRAPHQL_QUERY, "variables": {"login": username}}).encode()
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "profile-contribution-city",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"][0].get("message", "GitHub GraphQL error"))
    user = payload.get("data", {}).get("user")
    if not user:
        raise RuntimeError(f"GitHub user not found: {username}")

    calendar = user["contributionsCollection"]["contributionCalendar"]
    weeks = []
    for week in calendar["weeks"][-53:]:
        days = [0] * 7
        for day in week["contributionDays"]:
            days[int(day["weekday"])] = int(day["contributionCount"])
        weeks.append(days)
    while len(weeks) < 53:
        weeks.insert(0, [0] * 7)

    languages = Counter()
    language_colors = {}
    for repository in user["repositories"]["nodes"]:
        language = repository.get("primaryLanguage")
        if language:
            languages[language["name"]] += 1
            language_colors[language["name"]] = language.get("color") or "#36e8ff"

    return {
        "weeks": weeks,
        "total": int(calendar["totalContributions"]),
        "repositories": int(user["repositories"]["totalCount"]),
        "followers": int(user["followers"]["totalCount"]),
        "languages": [(name, count, language_colors[name]) for name, count in languages.most_common(4)],
    }


def mock_data(username: str) -> dict:
    seed = int(hashlib.sha256(username.encode()).hexdigest()[:16], 16)
    rng = random.Random(seed)
    weeks = []
    for week in range(53):
        days = []
        momentum = 0.4 + 0.6 * (week / 52)
        for weekday in range(7):
            if weekday in (0, 6):
                value = rng.choices((0, 1, 2, 4), weights=(6, 3, 1, 1))[0]
            else:
                value = max(0, round(rng.gauss(2.2 * momentum, 2.0)))
            days.append(value)
        weeks.append(days)
    total = sum(sum(week) for week in weeks)
    return {
        "weeks": weeks,
        "total": total,
        "repositories": 24,
        "followers": 18,
        "languages": [("C#", 11, "#178600"), ("Python", 6, "#3572A5"), ("JavaScript", 5, "#f1e05a"), ("C++", 2, "#f34b7d")],
    }


def level_for(count: int) -> int:
    if count <= 0:
        return 0
    if count == 1:
        return 1
    if count <= 3:
        return 2
    if count <= 6:
        return 3
    return 4


def polygon(points: list[tuple[float, float]], fill: str, opacity: float = 1.0) -> str:
    value = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{value}" fill="{fill}" fill-opacity="{opacity:.2f}"/>'


def short_label(value: str, limit: int = 16) -> str:
    """Keep external labels inside the fixed-width statistics panel."""
    return value if len(value) <= limit else f"{value[: limit - 1]}…"


def cube(x: float, y: float, height: float, level: int) -> str:
    half_w = 5.8
    half_h = 3.1
    tops = ("#101a35", "#16475a", "#167c8d", "#25b9c7", "#6cf4ff")
    lefts = ("#0a1124", "#103341", "#105a67", "#177f88", "#30aab2")
    rights = ("#0d1730", "#123c50", "#136a79", "#199aa7", "#3cc9d2")
    top = [(x, y - height), (x + half_w, y + half_h - height), (x, y + 2 * half_h - height), (x - half_w, y + half_h - height)]
    left = [(x - half_w, y + half_h - height), (x, y + 2 * half_h - height), (x, y + 2 * half_h), (x - half_w, y + half_h)]
    right = [(x + half_w, y + half_h - height), (x, y + 2 * half_h - height), (x, y + 2 * half_h), (x + half_w, y + half_h)]
    glow = 0.38 if level == 4 else 0
    return "".join(
        (
            polygon(left, lefts[level]),
            polygon(right, rights[level]),
            polygon(top, tops[level]),
            f'<circle cx="{x:.1f}" cy="{y-height+half_h:.1f}" r="7" fill="#54efff" opacity="{glow:.2f}" filter="url(#glow)"/>' if glow else "",
        )
    )


def render_svg(data: dict, username: str, display_name: str) -> str:
    width, height = 1000, 390
    cells = []
    heights = (2, 6, 12, 20, 29)
    for week_index, week in enumerate(data["weeks"][-53:]):
        for weekday, count in enumerate(week):
            level = level_for(int(count))
            x = 125 + (week_index - weekday) * 8.25
            y = 94 + (week_index + weekday) * 4.25
            cells.append((y, cube(x, y, heights[level], level)))
    cells.sort(key=lambda item: item[0])
    city = "".join(shape for _, shape in cells)

    languages = data.get("languages") or []
    language_rows = []
    for index, (name, count, color) in enumerate(languages[:4]):
        y = 270 + index * 22
        safe_language = escape(short_label(str(name)))
        language_rows.append(
            f'<circle cx="719" cy="{y-4}" r="4" fill="{escape(color)}"/>'
            f'<text x="732" y="{y}" class="small">{safe_language}</text>'
            f'<text x="934" y="{y}" class="small value" text-anchor="end">{int(count)} depo</text>'
        )

    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    safe_name = escape(display_name.upper())
    safe_user = escape(username)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{safe_name} GitHub katkı şehri</title>
  <desc id="desc">{int(data['total'])} gerçek GitHub katkısından oluşturulan izometrik şehir.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#060b18"/>
      <stop offset="0.55" stop-color="#08142a"/>
      <stop offset="1" stop-color="#120d2c"/>
    </linearGradient>
    <linearGradient id="line" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#36e8ff" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#36e8ff" stop-opacity="0.7"/>
      <stop offset="1" stop-color="#9c6aff" stop-opacity="0"/>
    </linearGradient>
    <filter id="glow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="6"/>
    </filter>
    <style>
      .label {{ fill: #8eaac5; font: 600 11px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; letter-spacing: 1.2px; }}
      .title {{ fill: #eefaff; font: 800 24px Inter, ui-sans-serif, system-ui, sans-serif; letter-spacing: 0.5px; }}
      .number {{ fill: #eefaff; font: 800 27px Inter, ui-sans-serif, system-ui, sans-serif; }}
      .small {{ fill: #a9bfd4; font: 500 11px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
      .value {{ fill: #55eaff; }}
      .scan {{ animation: scan 5s ease-in-out infinite; }}
      .pulse {{ animation: pulse 2.8s ease-in-out infinite; transform-origin: center; }}
      @keyframes scan {{ 0%, 100% {{ opacity: 0.15; }} 50% {{ opacity: 0.75; }} }}
      @keyframes pulse {{ 0%, 100% {{ opacity: 0.55; }} 50% {{ opacity: 1; }} }}
    </style>
  </defs>
  <rect width="1000" height="390" rx="24" fill="url(#bg)"/>
  <rect x="1" y="1" width="998" height="388" rx="23" fill="none" stroke="#36e8ff" stroke-opacity="0.2"/>
  <text x="34" y="34" class="label">{safe_name} // KATKI ŞEHRİ</text>
  <text x="34" y="50" class="small">@{safe_user} · SON GÜNCELLEME {today}</text>
  <path class="scan" d="M32 62H968" stroke="url(#line)" stroke-width="2"/>

  <g opacity="0.32">
    <path d="M91 111L553 349" stroke="#36e8ff" stroke-opacity="0.16"/>
    <path d="M150 86L611 324" stroke="#9c6aff" stroke-opacity="0.13"/>
  </g>
  <g>{city}</g>

  <rect x="684" y="85" width="282" height="266" rx="18" fill="#071226" fill-opacity="0.84" stroke="#36e8ff" stroke-opacity="0.2"/>
  <text x="711" y="113" class="label">SON 12 AY</text>
  <text x="711" y="148" class="number pulse">{int(data['total']):,}</text>
  <text x="711" y="168" class="small">KATKI</text>

  <line x1="711" y1="189" x2="939" y2="189" stroke="#8eaac5" stroke-opacity="0.18"/>
  <text x="711" y="215" class="number">{int(data['repositories'])}</text>
  <text x="711" y="233" class="small">HERKESE AÇIK DEPO</text>
  <text x="873" y="215" class="number">{int(data['followers'])}</text>
  <text x="873" y="233" class="small">TAKİPÇİ</text>

  <text x="711" y="259" class="label">ÖNE ÇIKAN DİLLER</text>
  {''.join(language_rows)}

  <text x="34" y="372" class="small">AZ ETKİNLİK</text>
  <rect x="111" y="363" width="14" height="8" rx="2" fill="#16475a"/>
  <rect x="131" y="363" width="14" height="8" rx="2" fill="#167c8d"/>
  <rect x="151" y="363" width="14" height="8" rx="2" fill="#25b9c7"/>
  <rect x="171" y="363" width="14" height="8" rx="2" fill="#6cf4ff"/>
  <text x="194" y="372" class="small">YÜKSEK ETKİNLİK</text>
</svg>
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", required=True)
    parser.add_argument("--display-name", default="ENES YÜREKLİ")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--offline", action="store_true", help="Render deterministic demo data without GitHub access")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    token = os.environ.get("GITHUB_TOKEN", "")
    if args.offline:
        data = mock_data(args.username)
    else:
        if not token:
            sys.exit("GITHUB_TOKEN is required unless --offline is used")
        try:
            data = github_data(args.username, token)
        except (urllib.error.URLError, RuntimeError, KeyError, ValueError) as error:
            sys.exit(f"Could not build dashboard: {error}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_svg(data, args.username, args.display_name), encoding="utf-8")
    print(f"Katkı şehri oluşturuldu: {args.output}")


if __name__ == "__main__":
    main()
