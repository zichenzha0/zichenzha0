#!/usr/bin/env python3
"""Refresh the live commit feed between the LIVE-ACTIVITY markers in README.md."""
import datetime as dt
import os
import re
from zoneinfo import ZoneInfo

import requests

USER = os.environ.get("GH_USER", "zichenzha0")
TOKEN = os.environ.get("GH_TOKEN", "")
README = os.environ.get("README", "README.md")
MAX_ROWS = 6
REPOS_TO_SCAN = 10
# Private repos allowed to appear in the feed (everything else private stays hidden).
SHOW_PRIVATE = {n.strip().lower() for n in os.environ.get("SHOW_PRIVATE", "dawntale,dawntale-community").split(",") if n.strip()}
TZ = ZoneInfo("America/New_York")
START, END = "<!--LIVE-ACTIVITY:START-->", "<!--LIVE-ACTIVITY:END-->"

S = requests.Session()
S.headers.update({"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})
if TOKEN:
    S.headers["Authorization"] = f"Bearer {TOKEN}"


def get(url, **params):
    r = S.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def ago(when, now):
    s = int((now - when).total_seconds())
    if s < 3600:
        return f"{max(s // 60, 1)} min ago"
    if s < 86400:
        return f"{s // 3600} h ago"
    d = s // 86400
    return "yesterday" if d == 1 else f"{d} days ago"


def latest_commits():
    try:  # a personal token can also see the allowed private repos
        repos = get("https://api.github.com/user/repos", sort="pushed", per_page=100, affiliation="owner")
    except requests.HTTPError:  # default Actions token: public repos only
        repos = get(f"https://api.github.com/users/{USER}/repos", sort="pushed", per_page=100, type="owner")
    repos = [
        r for r in repos
        if not r["fork"] and r["name"].lower() != USER.lower()
        and r["owner"]["login"].lower() == USER.lower()
        and (not r["private"] or r["name"].lower() in SHOW_PRIVATE)
    ][:REPOS_TO_SCAN]
    rows = []
    for repo in repos:
        try:
            commits = get(f"https://api.github.com/repos/{repo['full_name']}/commits", author=USER, per_page=5)
        except requests.HTTPError:
            continue
        for c in commits:
            when = dt.datetime.fromisoformat(c["commit"]["author"]["date"].replace("Z", "+00:00"))
            msg = c["commit"]["message"].splitlines()[0].strip() or "update"
            msg = (msg[:57] + "…") if len(msg) > 58 else msg
            msg = msg.replace("|", "\\|").replace("[", "(").replace("]", ")")
            name = ("🔒 " if repo["private"] else "") + repo["name"]
            rows.append((when, name, repo["html_url"], msg, c["html_url"]))
    rows.sort(key=lambda x: x[0], reverse=True)
    return rows[:MAX_ROWS]


def contribution_counts():
    """Total contributions (includes private ones when the profile setting is on)."""
    if not TOKEN:
        return None
    q = """query($login:String!){user(login:$login){contributionsCollection{
      contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""
    r = S.post("https://api.github.com/graphql", json={"query": q, "variables": {"login": USER}}, timeout=30)
    r.raise_for_status()
    cal = r.json()["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    return sum(d["contributionCount"] for d in days[-7:]), cal["totalContributions"]


def render():
    now = dt.datetime.now(dt.timezone.utc)
    lines = ["", "| | Repo | Latest commit | When |", "|:-:|:--|:--|--:|"]
    for i, (when, name, url, msg, curl) in enumerate(latest_commits()):
        dot = "🟠" if (now - when).days < 1 else ("🟡" if (now - when).days < 7 else "⚪")
        lines.append(f"| {dot} | [{name}]({url}) | [{msg}]({curl}) | {ago(when, now)} |")
    if len(lines) == 3:
        lines.append("| ⚪ | — | Quiet on public repos right now — building in private | — |")
    stamp = now.astimezone(TZ).strftime("%b %d, %I:%M %p ET").replace(" 0", " ")
    counts = contribution_counts()
    stat = f"📈 <b>{counts[0]}</b> contributions this week · <b>{counts[1]:,}</b> in the past year · " if counts else ""
    lines += ["", f'<p align="center"><sub>{stat}🔄 auto-synced {stamp}</sub></p>', ""]
    return "\n".join(lines)


def main():
    with open(README, encoding="utf-8") as f:
        text = f.read()
    new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: START + render() + END, text, flags=re.S)
    with open(README, "w", encoding="utf-8") as f:
        f.write(new)


if __name__ == "__main__":
    main()
