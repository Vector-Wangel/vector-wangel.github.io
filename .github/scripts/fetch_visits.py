"""Fetch visit stats from GoatCounter and write visits.json for the homepage."""
import json, os, sys, urllib.parse, urllib.request
import pycountry

SITE = os.environ.get("GOATCOUNTER_SITE", "https://vectorwang.goatcounter.com")
TOKEN = os.environ["GOATCOUNTER_TOKEN"]
START = "2020-01-01T00:00:00Z"


def get(path, **params):
    q = urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(f"{SITE}/api/v0/{path}?{q}", headers={"Authorization": f"Bearer {TOKEN}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


total = get("stats/total", start=START).get("total", 0)

countries, exclude = [], []
while True:
    page = get("stats/locations", start=START, limit=100, exclude=exclude)
    rows = page.get("stats", [])
    for r in rows:
        exclude.append(r["id"])
        c = pycountry.countries.get(alpha_2=r["id"].upper()) if len(r["id"]) == 2 else None
        if c:  # skips "Unknown"
            countries.append({"id": c.numeric, "code": c.alpha_2, "name": r["name"], "count": r["count"]})
    if not page.get("more") or not rows:
        break

countries.sort(key=lambda c: -c["count"])
out = {"total": total, "countries": countries}
with open("visits.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f"visits.json: total={total}, countries={len(countries)}", file=sys.stderr)
