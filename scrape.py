# Pulls Mizzou's game history from the CollegeFootballData API into data/games.json.
# Stdlib only. Setup: get a free key at https://collegefootballdata.com/key, then:
#   export CFBD_KEY=your_key_here
#   python3 scrape.py
import json, os, urllib.request, urllib.error, urllib.parse, datetime

KEY = os.environ.get("CFBD_KEY")
if not KEY:
    raise SystemExit("Set your key first:  export CFBD_KEY=your_key_here")

os.makedirs("data", exist_ok=True)
games = []
for year in range(1890, datetime.date.today().year + 1):
    qs = urllib.parse.urlencode({"year": year, "team": "Missouri", "seasonType": "both"})
    req = urllib.request.Request("https://api.collegefootballdata.com/games?" + qs,
                                 headers={"Authorization": "Bearer " + KEY})
    try:
        rows = json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{year}: HTTP {e.code} (401 = bad key, 429 = out of calls)")
    n = 0
    for g in rows:
        home, away = g.get("homeTeam") or g.get("home_team"), g.get("awayTeam") or g.get("away_team")
        hp, ap = g.get("homePoints", g.get("home_points")), g.get("awayPoints", g.get("away_points"))
        if hp is None or ap is None: continue
        mizzou_home = home == "Missouri"
        games.append({"season": year,
                      "date": (g.get("startDate") or g.get("start_date") or "")[:10],
                      "opp": away if mizzou_home else home,
                      "loc": "N" if (g.get("neutralSite") or g.get("neutral_site")) else ("H" if mizzou_home else "A"),
                      "us": hp if mizzou_home else ap,
                      "them": ap if mizzou_home else hp})
        n += 1
    print(year, n, "games")

json.dump(games, open("data/games.json", "w"))
print("Wrote", len(games), "games to data/games.json")