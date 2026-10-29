"""Рисует карточки статистики (cards/stats.svg и cards/langs.svg) из GitHub API."""
import json, os, urllib.request
from html import escape

USER = os.environ["GH_USER"]
TOKEN = os.environ["GH_TOKEN"]
SKIP_REPOS = {"Sem1-2025", "SEM2"}          # не учитывать в языках
SKIP_LANGS = {"Rich Text Format"}

BG, TITLE, TEXT, ICON = "#1a1b27", "#70a5fd", "#38bdae", "#bf91f3"
FONT = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"

QUERY = """
query($login: String!) {
  user(login: $login) {
    name login
    pullRequests { totalCount }
    issues { totalCount }
    contributionsCollection { totalCommitContributions restrictedContributionsCount }
    repositoriesContributedTo(contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      nodes {
        name stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}"""

ICONS = {
    "star": "M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25zm0 2.445L6.615 5.5a.75.75 0 01-.564.41l-3.097.45 2.24 2.184a.75.75 0 01.216.664l-.528 3.084 2.769-1.456a.75.75 0 01.698 0l2.77 1.456-.53-3.084a.75.75 0 01.216-.664l2.24-2.183-3.096-.45a.75.75 0 01-.564-.41L8 2.694z",
    "commit": "M1.643 3.143L.427 1.927A.25.25 0 000 2.104V5.75c0 .138.112.25.25.25h3.646a.25.25 0 00.177-.427L2.715 4.215a6.5 6.5 0 11-1.18 4.458.75.75 0 10-1.493.154 8.001 8.001 0 101.6-5.684zM7.75 4a.75.75 0 01.75.75v2.992l2.028.812a.75.75 0 01-.557 1.392l-2.5-1A.75.75 0 017 8.25v-3.5A.75.75 0 017.75 4z",
    "pr": "M7.177 3.073L9.573.677A.25.25 0 0110 .854v4.792a.25.25 0 01-.427.177L7.177 3.427a.25.25 0 010-.354zM3.75 2.5a.75.75 0 100 1.5.75.75 0 000-1.5zm-2.25.75a2.25 2.25 0 113 2.122v5.256a2.251 2.251 0 11-1.5 0V5.372A2.25 2.25 0 011.5 3.25zM11 2.5h-1V4h1a1 1 0 011 1v5.628a2.251 2.251 0 101.5 0V5A2.5 2.5 0 0011 2.5zm1 10.25a.75.75 0 111.5 0 .75.75 0 01-1.5 0zM3.75 12a.75.75 0 100 1.5.75.75 0 000-1.5z",
    "issue": "M8 9.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3zM8 0a8 8 0 100 16A8 8 0 008 0zM1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0z",
    "repo": "M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 011-1h8zM5 12.25v3.25a.25.25 0 00.4.2l1.45-1.087a.25.25 0 01.3 0L8.6 15.7a.25.25 0 00.4-.2v-3.25a.25.25 0 00-.25-.25h-3.5a.25.25 0 00-.25.25z",
}


def fetch():
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={
        "Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    data = json.load(urllib.request.urlopen(req))
    if "errors" in data:
        raise SystemExit(f"GitHub API error: {data['errors']}")
    return data["data"]["user"]


def card(width, height, inner):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" font-family="{FONT}">'
            f'<rect width="{width}" height="{height}" rx="12" fill="{BG}"/>{inner}</svg>')


def stats_svg(u):
    cc = u["contributionsCollection"]
    rows = [
        ("star", "Total Stars Earned", sum(r["stargazerCount"] for r in u["repositories"]["nodes"])),
        ("commit", "Total Commits (last year)", cc["totalCommitContributions"] + cc["restrictedContributionsCount"]),
        ("pr", "Total PRs", u["pullRequests"]["totalCount"]),
        ("issue", "Total Issues", u["issues"]["totalCount"]),
        ("repo", "Contributed to (last year)", u["repositoriesContributedTo"]["totalCount"]),
    ]
    name = escape(u["name"] or u["login"])
    out = [f'<text x="25" y="38" fill="{TITLE}" font-size="18" font-weight="600">{name}\'s GitHub Stats</text>']
    for i, (icon, label, value) in enumerate(rows):
        y = 72 + i * 25
        out.append(f'<path transform="translate(25 {y - 12})" fill="{ICON}" fill-rule="evenodd" d="{ICONS[icon]}"/>')
        out.append(f'<text x="50" y="{y}" fill="{TEXT}" font-size="14" font-weight="600">{label}:</text>')
        out.append(f'<text x="270" y="{y}" fill="{TEXT}" font-size="14" font-weight="700">{value}</text>')
    return card(340, 195, "".join(out))


def langs_svg(u):
    sizes, colors = {}, {}
    for repo in u["repositories"]["nodes"]:
        if repo["name"] in SKIP_REPOS:
            continue
        for e in repo["languages"]["edges"]:
            n = e["node"]["name"]
            if n in SKIP_LANGS:
                continue
            sizes[n] = sizes.get(n, 0) + e["size"]
            colors[n] = e["node"]["color"] or "#858585"
    top = sorted(sizes.items(), key=lambda kv: -kv[1])[:6]
    total = sum(s for _, s in top) or 1

    out = [f'<text x="25" y="38" fill="{TITLE}" font-size="18" font-weight="600">Most Used Languages</text>',
           '<clipPath id="bar"><rect x="25" y="55" width="250" height="8" rx="4"/></clipPath><g clip-path="url(#bar)">']
    x = 25.0
    for n, s in top:
        w = 250 * s / total
        out.append(f'<rect x="{x:.2f}" y="55" width="{w + 0.5:.2f}" height="8" fill="{colors[n]}"/>')
        x += w
    out.append("</g>")
    for i, (n, s) in enumerate(top):
        cx, cy = 25 + (i % 2) * 135, 90 + (i // 2) * 30
        out.append(f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{colors[n]}"/>')
        out.append(f'<text x="{cx + 16}" y="{cy}" fill="{TEXT}" font-size="12">{escape(n)} {100 * s / total:.2f}%</text>')
    return card(300, 195, "".join(out))


if __name__ == "__main__":
    user = fetch()
    os.makedirs("cards", exist_ok=True)
    for name, svg in (("stats", stats_svg(user)), ("langs", langs_svg(user))):
        with open(f"cards/{name}.svg", "w", encoding="utf-8") as f:
            f.write(svg)
