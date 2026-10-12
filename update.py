#!/usr/bin/env python3
"""Downloads the world's map.sql, estimates alliance control per region and writes data.json.

Usage:  python update.py              (downloads from WORLD)
        python update.py --file map.sql   (use a local copy, for testing)
"""
import re, json, gzip, sys, os, urllib.request, datetime, collections

WORLD = "https://rog.x3.international.travian.com"   # change this if you move to another world
THRESHOLD = 51.0                                     # % of alliance-member population needed to count as controlled
RENAME = {"Brundisium": "Brandisium"}                # region names that differ between map.sql and the map
UNLOCK_POP = 4000                                    # a region unlocks for good once its population reaches this
HERE = os.path.dirname(os.path.abspath(__file__))

# ---- colours: a fixed slot per alliance, remembered in colors.json so colours never change between days
BASES = [10, 34, 58, 82, 106, 130, 154, 178, 202, 226, 250, 274, 298, 322, 346]
VARIANTS = [(.80, .095, .70, .095), (.72, .105, .62, .105), (.88, .07, .78, .07)]   # L, C light, L, C dark
SLOTS = [(h + 12, *v) for v in VARIANTS for h in BASES]

def load_sql():
    if "--file" in sys.argv:
        raw = open(sys.argv[sys.argv.index("--file") + 1], "rb").read()
    else:
        req = urllib.request.Request(WORLD + "/map.sql", headers={"User-Agent": "alliance-map-daily/1.0", "Accept-Encoding": "gzip"})
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", "replace")

TOK = re.compile(r"'((?:[^'\\]|\\.|'')*)'|(-?\d+)|(TRUE|FALSE|NULL)")

def parse(text):
    rows = []
    for line in text.splitlines():
        m = re.search(r"VALUES \((.*)\);\s*$", line)
        if not m:
            continue
        vals = []
        for t in TOK.finditer(m.group(1)):
            s, n, k = t.groups()
            vals.append(s.replace("''", "'") if s is not None else int(n) if n is not None else k)
        if len(vals) >= 12:
            rows.append(vals)
    return rows

def main():
    rows = parse(load_sql())
    if len(rows) < 100:
        sys.exit(f"map.sql looks wrong ({len(rows)} rows), leaving data.json untouched")
    ov = json.load(open(os.path.join(HERE, "overrides.json")))
    prev_path = os.path.join(HERE, "data.json")
    prev = json.load(open(prev_path)) if os.path.exists(prev_path) else {}
    unlocked = set(prev.get("unlocked") or ov["start_unlocked"])   # unlocked regions are never locked again
    pop = collections.defaultdict(int)
    ally = collections.defaultdict(lambda: collections.Counter())
    for v in rows:
        region = RENAME.get(v[11], v[11])
        pop[region] += v[10]
        if v[9]:
            ally[region][v[9]] += v[10]
    regions = {}
    for r in pop:
        c = ally[r]
        members = sum(c.values())
        entry = {"st": "none", "al": "", "pct": None, "pop": pop[r], "members": members, "top": []}
        if members:
            ranked = c.most_common()
            lead, lead_pop = ranked[0]
            pct = round(100 * lead_pop / members, 2)
            entry.update(al=lead, pct=pct, top=[[t, round(100 * p / members, 1)] for t, p in ranked[:3]],
                         st="ctrl" if pct >= THRESHOLD else "part")
        regions[r] = entry
    force_locked, force_unlocked = set(ov["force_locked"]), set(ov["force_unlocked"])
    exact = None
    xp = os.path.join(HERE, "exact.json")
    if os.path.exists(xp):
        ex = json.load(open(xp))
        if datetime.datetime.now(datetime.timezone.utc) < datetime.datetime.fromisoformat(ex["valid_until"].replace("Z", "+00:00")):
            exact = ex
    unlocked |= {r for r, p in pop.items() if p >= UNLOCK_POP}
    unlocked = (unlocked | force_unlocked) - force_locked
    for r, e in regions.items():
        if e["pop"] > 0 and r not in unlocked:
            e["st"] = "lock"
    if exact:                                          # figures copied from the game win over the estimate until valid_until
        for r, e in exact["regions"].items():
            old = regions.get(r, {})
            regions[r] = {"st": e["st"], "al": e["al"], "pct": e["pct"], "pop": e["pop"],
                          "members": 0, "top": []}
        unlocked = {r for r, e in exact["regions"].items() if e["st"] in ("ctrl", "part")}

    # ---- colours
    cpath = os.path.join(HERE, "colors.json")
    colors = json.load(open(cpath)) if os.path.exists(cpath) else {}
    used = {(c["h"], c["l"], c["c"]) for c in colors.values()}
    leaders = collections.Counter(e["al"] for e in regions.values() if e["al"])
    for tag, _ in sorted(leaders.items(), key=lambda x: (-x[1], x[0])):
        if tag in colors:
            continue
        free = [s for s in SLOTS if (s[0], s[1], s[2]) not in used]
        h, l, c, dl, dc = free[0] if free else (SLOTS[len(colors) % len(SLOTS)][0] + 6, *SLOTS[len(colors) % len(SLOTS)][1:])
        colors[tag] = {"h": h, "l": l, "c": c, "dl": dl, "dc": dc}
        used.add((h, l, c))
    json.dump(colors, open(cpath, "w"), ensure_ascii=False, indent=1)
    alliances = {}
    for i, tag in enumerate(sorted(leaders)):
        alliances[tag] = dict(colors[tag], id=f"a{i}")
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = {"updated": exact["date"] if exact else now, "source": "game" if exact else "estimate",
           "world": WORLD, "threshold": THRESHOLD, "unlock_pop": UNLOCK_POP, "unlocked": sorted(unlocked), "villages": len(rows), "regions": regions, "alliances": alliances}
    json.dump(out, open(os.path.join(HERE, "data.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"ok: {len(rows)} villages, {len(regions)} regions, {len(alliances)} alliances")

if __name__ == "__main__":
    main()
