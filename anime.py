import datetime, json, os, re, urllib.parse, urllib.request

USER = os.environ["GH_USER"]
TOKEN = os.environ["GH_TOKEN"]
DAYS = 7 


RAW = "https://raw.githubusercontent.com/DmitrygitDueslik/DmitrygitDueslik/main/"

LEVELS = [
    (0,  RAW + "sleep.svg", "😴 Сплю…"),
    (1,  RAW + "walk.svg",  "🚶 Потихоньку иду к цели"),
    (10, RAW + "work.svg",  "🔥 Усердно работаю!"),
]

since = (datetime.date.today() - datetime.timedelta(days=DAYS)).isoformat()
q = urllib.parse.quote(f"author:{USER} author-date:>={since}")
req = urllib.request.Request(
    f"https://api.github.com/search/commits?q={q}&per_page=1",
    headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"},
)
count = json.load(urllib.request.urlopen(req))["total_count"]

need, gif, caption = [lvl for lvl in LEVELS if count >= lvl[0]][-1]

STATS = ("https://github-readme-stats.vercel.app/api?username=" + USER +
         "&show_icons=true&theme=tokyonight&hide_border=true&border_radius=12&locale=ru&hide_rank=true")

block = f"""<!-- ANIME:START -->
<p align="center">
  <img height="170" src="{STATS}" />
  <img height="170" src="{gif}" />
</p>
<p align="center"><sub>{caption} · коммитов за {DAYS} дней: {count}</sub></p>
<!-- ANIME:END -->"""

with open("README.md", encoding="utf-8") as f:
    readme = f.read()
readme = re.sub(r"<!-- ANIME:START -->.*?<!-- ANIME:END -->", lambda m: block, readme, flags=re.S)
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
