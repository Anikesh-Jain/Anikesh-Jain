import os
import json
import urllib.request
from collections import Counter

USER = "Anikesh-Jain"
TOKEN = os.environ["GITHUB_TOKEN"]

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "Anikesh-Jain-profile"
}

def api(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

user = api(f"https://api.github.com/users/{USER}")

repos = []
page = 1

while True:
    data = api(
        f"https://api.github.com/users/{USER}/repos"
        f"?per_page=100&page={page}&type=owner"
    )

    if not data:
        break

    repos.extend(data)

    if len(data) < 100:
        break

    page += 1

languages = Counter()

for repo in repos:
    if repo.get("fork"):
        continue

    try:
        data = api(repo["languages_url"])

        for language, amount in data.items():
            languages[language] += amount

    except Exception:
        pass

total_code = sum(languages.values())
top_languages = languages.most_common(6)

def esc(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

followers = user.get("followers", 0)
public_repos = user.get("public_repos", 0)

os.makedirs("profile", exist_ok=True)

# -----------------------------
# GitHub Statistics
# -----------------------------

top_language = top_languages[0][0] if top_languages else "N/A"

stats = f'''<svg xmlns="http://www.w3.org/2000/svg" width="576" height="200" viewBox="0 0 576 200">
<rect width="576" height="200" rx="10" fill="#1a1b27"/>

<text x="28" y="38" fill="#70a5fd" font-family="Segoe UI,Arial" font-size="20" font-weight="700">
GitHub Statistics
</text>

<text x="28" y="82" fill="#858585" font-family="Segoe UI,Arial" font-size="13">
Public Repositories
</text>

<text x="28" y="108" fill="#38bdae" font-family="Segoe UI,Arial" font-size="23" font-weight="700">
{public_repos}
</text>

<text x="205" y="82" fill="#858585" font-family="Segoe UI,Arial" font-size="13">
Followers
</text>

<text x="205" y="108" fill="#38bdae" font-family="Segoe UI,Arial" font-size="23" font-weight="700">
{followers}
</text>

<text x="350" y="82" fill="#858585" font-family="Segoe UI,Arial" font-size="13">
Repositories Scanned
</text>

<text x="350" y="108" fill="#38bdae" font-family="Segoe UI,Arial" font-size="23" font-weight="700">
{len(repos)}
</text>

<line x1="28" y1="132" x2="548" y2="132" stroke="#30363d"/>

<text x="28" y="160" fill="#858585" font-family="Segoe UI,Arial" font-size="13">
Top Language
</text>

<text x="28" y="184" fill="#70a5fd" font-family="Segoe UI,Arial" font-size="17" font-weight="600">
{esc(top_language)}
</text>

<text x="205" y="160" fill="#858585" font-family="Segoe UI,Arial" font-size="13">
Languages Detected
</text>

<text x="205" y="184" fill="#70a5fd" font-family="Segoe UI,Arial" font-size="17" font-weight="600">
{len(top_languages)}
</text>

<text x="350" y="160" fill="#858585" font-family="Segoe UI,Arial" font-size="13">
Code Tracked
</text>

<text x="350" y="184" fill="#70a5fd" font-family="Segoe UI,Arial" font-size="17" font-weight="600">
{total_code:,}
</text>

</svg>'''

with open("profile/stats.svg", "w", encoding="utf-8") as f:
    f.write(stats)

# -----------------------------
# Top Languages
# -----------------------------

width = 400
height = max(120, 70 + len(top_languages) * 32)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="{width}" height="{height}" rx="10" fill="#1a1b27"/>

<text x="24" y="36" fill="#70a5fd" font-family="Segoe UI,Arial" font-size="20" font-weight="700">
Top Languages
</text>
'''

y = 70

for language, amount in top_languages:

    percentage = (amount / total_code * 100) if total_code else 0
    bar_width = 326 * percentage / 100

    svg += f'''
<text x="24" y="{y}" fill="#c9d1d9" font-family="Segoe UI,Arial" font-size="13">
{esc(language)}
</text>

<text x="350" y="{y}" text-anchor="end" fill="#858585" font-family="Segoe UI,Arial" font-size="12">
{percentage:.1f}%
</text>

<rect x="24" y="{y + 10}" width="326" height="7" rx="3.5" fill="#30363d"/>

<rect x="24" y="{y + 10}" width="{bar_width:.1f}" height="7" rx="3.5" fill="#70a5fd"/>
'''

    y += 32

svg += "</svg>"

with open("profile/top-langs.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print("Generated profile/stats.svg")
print("Generated profile/top-langs.svg")
print("Top languages:", top_languages)
