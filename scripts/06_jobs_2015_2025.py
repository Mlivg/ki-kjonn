"""Are women moving into the jobs where ChatGPT is used most?

Sorts 390 occupations by ChatGPT use per worker and splits them into five
groups, each with about a fifth of 2025 employment. The groups stay fixed.
Then it compares where women and men worked in 2015 and in 2025.

Main measure, fixed before the first run: the share of employed women who work
in the highest-use fifth, in 2015 and 2025, compared with the same share for men.

Second measure: the share of work messages that would come from women if each
job used ChatGPT as much as today, using each year's employment. For 2025 this
must reproduce 49.18 %, a number from analysis 01, before it is used.

Use per worker comes from job tasks, not from observed use. It is held fixed at
today's level for every year.

Reads only data/raw. Writes to output/.
Uses the Python standard library only. The tests on made-up data run first.
If one fails, the script stops before it reads the real data.

Run from the project folder:
    python3 -I scripts/06_jobs_2015_2025.py
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "output"
YEARS = [str(y) for y in range(2015, 2026)]


# ---------------------------------------------------------------------------
# The method.
# ---------------------------------------------------------------------------
def make_groups(use, size, n_groups):
    """Split occupations into n_groups by use, from highest to lowest.

    Each group holds about the same total size. An occupation goes to the group
    where the middle of its employment falls. Returns {occupation: group},
    with group 1 as the highest use.
    """
    order = sorted(use, key=lambda o: (-use[o], o))
    total = sum(size[o] for o in order)
    groups, running = {}, 0
    for o in order:
        middle = running + size[o] / 2
        groups[o] = min(n_groups, int(middle / total * n_groups) + 1)
        running += size[o]
    return groups


def share_in_group(counts, groups, group, denominator=None):
    """Share of the people in `counts` who work in occupations of this group."""
    inside = sum(c for o, c in counts.items() if groups.get(o) == group)
    return inside / (denominator if denominator is not None else sum(counts.values()))


def implied_women_share(use_women, use_men, women, men):
    """Share of messages from women if each job used ChatGPT at the given rates."""
    from_women = sum(use_women[o] * women.get(o, 0) for o in use_women)
    from_men = sum(use_men[o] * men.get(o, 0) for o in use_men)
    return from_women / (from_women + from_men)


# ---------------------------------------------------------------------------
# Tests on made-up data, where the right answer is known.
# ---------------------------------------------------------------------------
def close(a, b):
    return abs(a - b) < 1e-9


def run_tests():
    use = {"A": 3.0, "B": 2.0, "C": 1.0, "D": 0.5}
    size = {"A": 25, "B": 25, "C": 25, "D": 25}
    groups = make_groups(use, size, 4)
    assert groups == {"A": 1, "B": 2, "C": 3, "D": 4}, "groups by use"
    assert make_groups(use, size, 2) == {"A": 1, "B": 1, "C": 2, "D": 2}, "two groups"
    # A large occupation in the middle goes where its midpoint falls.
    assert make_groups({"A": 3.0, "B": 2.0, "C": 1.0}, {"A": 10, "B": 70, "C": 20}, 2)["B"] == 1, "midpoint rule"
    # B starts at 40 % of employment but its middle is at 55 %, so it belongs to the second half.
    assert make_groups({"A": 3.0, "B": 2.0, "C": 1.0}, {"A": 40, "B": 30, "C": 30}, 2)["B"] == 2, "midpoint, not start"

    women = {"A": 10, "B": 30, "C": 40, "D": 20}
    assert close(share_in_group(women, groups, 1), 0.10), "share in group"
    assert close(share_in_group(women, groups, 1, denominator=200), 0.05), "share with a wider denominator"

    # Equal use everywhere: the implied share equals women's share of employment.
    flat = {o: 1.0 for o in use}
    men = {"A": 40, "B": 20, "C": 10, "D": 30}
    assert close(implied_women_share(flat, flat, women, men), 100 / 200), "flat use"
    # Use only in A: the implied share equals women's share in A.
    only_a = {"A": 1.0, "B": 0.0, "C": 0.0, "D": 0.0}
    assert close(implied_women_share(only_a, only_a, women, men), 10 / 50), "use in one job"
    # Different use for women and men: 10 women using 3 against 10 men using 1 gives 30 / 40.
    assert close(implied_women_share({"A": 3.0}, {"A": 1.0}, {"A": 10}, {"A": 10}), 0.75), "separate use for women and men"


run_tests()
print("Tests on made-up data passed.\n")


# ---------------------------------------------------------------------------
# Real data.
# ---------------------------------------------------------------------------
def read(name):
    with open(RAW / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


occupations = read("styrk08_openai_gender_persons.csv")
assert len(occupations) == 390, "expected 390 occupations"
use = {o["styrk08"]: float(o["use_per_worker"]) for o in occupations}
use_women = {o["styrk08"]: float(o["use_women"]) for o in occupations}
use_men = {o["styrk08"]: float(o["use_men"]) for o in occupations}

women, men = {y: {} for y in YEARS}, {y: {} for y in YEARS}
for r in read("ssb_12542_sysselsatte_yrke4_kjonn.csv"):
    assert r["arbeidstid"] == "sum", "expected only the sum over working hours"
    assert r["kjonn"] in ("kvinner", "menn"), "unexpected value in the gender column"
    (women if r["kjonn"] == "kvinner" else men)[r["year"]][r["styrk08"]] = int(r["employed"])
assert set(women) == set(YEARS), "expected 2015 to 2025"
# The occupation file's women and men must equal SSB 2025.
assert all(women["2025"][o["styrk08"]] == int(o["women"]) and men["2025"][o["styrk08"]] == int(o["men"])
           for o in occupations), "occupation file differs from SSB 2025"


def in_file(counts):
    """Only the 390 occupations with a use value. Code 0000 (unknown) is not among them."""
    return {o: counts.get(o, 0) for o in use}


# Check before use: the implied share for 2025 must reproduce analysis 01.
implied = {y: implied_women_share(use, use, in_file(women[y]), in_file(men[y])) for y in YEARS}
assert abs(100 * implied["2025"] - 49.18) < 0.005, "implied share does not reproduce 49.18 % for 2025"
implied_gender = {y: implied_women_share(use_women, use_men, in_file(women[y]), in_file(men[y])) for y in YEARS}


def run(name, description, group_year, n_groups, wide_denominator=False):
    size = {o: women[group_year].get(o, 0) + men[group_year].get(o, 0) for o in use}
    groups = make_groups(use, size, n_groups)
    out = {"name": name, "description": description, "groups": groups, "n_groups": n_groups}
    for y in ("2015", "2025"):
        w, m = in_file(women[y]), in_file(men[y])
        w_den = sum(women[y].values()) if wide_denominator else None
        m_den = sum(men[y].values()) if wide_denominator else None
        out[f"women_top_{y}"] = share_in_group(w, groups, 1, w_den)
        out[f"men_top_{y}"] = share_in_group(m, groups, 1, m_den)
        inside_w = sum(c for o, c in w.items() if groups[o] == 1)
        inside_m = sum(c for o, c in m.items() if groups[o] == 1)
        out[f"women_share_inside_top_{y}"] = inside_w / (inside_w + inside_m)
    out["employment_share_of_top"] = sum(size[o] for o in use if groups[o] == 1) / sum(size.values())
    return out


# The first row is the main result, chosen before any row was run.
runs = [
    run("main", "Top fifth by use, groups set on 2025 employment", "2025", 5),
    run("groups_2015", "Top fifth by use, groups set on 2015 employment", "2015", 5),
    run("top_tenth", "Top tenth by use, groups set on 2025 employment", "2025", 10),
    run("all_codes", "Top fifth, shares of all employed, including code 0000 and codes without a use value", "2025", 5, True),
]
main = runs[0]

# Women's share inside each of the five groups, main grouping.
by_group = []
for g in range(1, 6):
    row = {"group": g}
    for y in ("2015", "2025"):
        w = sum(c for o, c in in_file(women[y]).items() if main["groups"][o] == g)
        m = sum(c for o, c in in_file(men[y]).items() if main["groups"][o] == g)
        row[f"women_share_{y}"] = w / (w + m)
        row[f"women_{y}"], row[f"men_{y}"] = w, m
    lo = min(use[o] for o in use if main["groups"][o] == g)
    hi = max(use[o] for o in use if main["groups"][o] == g)
    row["use_range"] = (lo, hi)
    by_group.append(row)

# Every year, main grouping.
yearly = []
for y in YEARS:
    w, m = in_file(women[y]), in_file(men[y])
    yearly.append({"year": y, "women_top": share_in_group(w, main["groups"], 1), "men_top": share_in_group(m, main["groups"], 1),
                   "implied": implied[y], "implied_gender": implied_gender[y],
                   "women_share_employed": sum(w.values()) / (sum(w.values()) + sum(m.values()))})

OUT.mkdir(exist_ok=True)
pct = lambda v: round(100 * v, 2)
with open(OUT / "06_jobs_2015_2025.csv", "w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f)
    wr.writerow(["spec", "description", "employment_share_of_top_group_pct",
                 "women_in_top_2015_pct", "women_in_top_2025_pct", "women_change",
                 "men_in_top_2015_pct", "men_in_top_2025_pct", "men_change",
                 "women_share_inside_top_2015_pct", "women_share_inside_top_2025_pct"])
    for r in runs:
        wr.writerow([r["name"], r["description"], pct(r["employment_share_of_top"]),
                     pct(r["women_top_2015"]), pct(r["women_top_2025"]), pct(r["women_top_2025"] - r["women_top_2015"]),
                     pct(r["men_top_2015"]), pct(r["men_top_2025"]), pct(r["men_top_2025"] - r["men_top_2015"]),
                     pct(r["women_share_inside_top_2015"]), pct(r["women_share_inside_top_2025"])])
with open(OUT / "06_jobs_2015_2025_yearly.csv", "w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f)
    wr.writerow(["year", "women_in_top_fifth_pct", "men_in_top_fifth_pct", "women_share_of_employed_pct",
                 "implied_women_share_of_messages_pct", "implied_with_gender_specific_use_pct"])
    for r in yearly:
        wr.writerow([r["year"], pct(r["women_top"]), pct(r["men_top"]), pct(r["women_share_employed"]),
                     pct(r["implied"]), pct(r["implied_gender"])])
with open(OUT / "06_jobs_2015_2025_groups.csv", "w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f)
    wr.writerow(["group", "use_per_worker_lowest", "use_per_worker_highest", "women_share_2015_pct", "women_share_2025_pct",
                 "change", "women_2015", "men_2015", "women_2025", "men_2025"])
    for r in by_group:
        wr.writerow([r["group"], round(r["use_range"][0], 3), round(r["use_range"][1], 3), pct(r["women_share_2015"]),
                     pct(r["women_share_2025"]), pct(r["women_share_2025"] - r["women_share_2015"]),
                     r["women_2015"], r["men_2015"], r["women_2025"], r["men_2025"]])

print(f"Check: implied women's share of messages, 2025 = {100 * implied['2025']:.2f} % (analysis 01: 49.18 %)\n")
print(f"{'spec':12} {'top size':>8} {'women 2015':>10} {'women 2025':>10} {'change':>7} {'men 2015':>8} {'men 2025':>8} {'change':>7}")
for r in runs:
    print(f"{r['name']:12} {100 * r['employment_share_of_top']:7.1f}% {100 * r['women_top_2015']:9.2f}% {100 * r['women_top_2025']:9.2f}% "
          f"{100 * (r['women_top_2025'] - r['women_top_2015']):+7.2f} {100 * r['men_top_2015']:7.2f}% {100 * r['men_top_2025']:7.2f}% "
          f"{100 * (r['men_top_2025'] - r['men_top_2015']):+7.2f}")
print("\nWomen's share inside each group, main grouping (group 1 = highest use)")
for r in by_group:
    print(f"  group {r['group']}  use {r['use_range'][0]:.2f} to {r['use_range'][1]:.2f}  "
          f"{100 * r['women_share_2015']:5.1f}% -> {100 * r['women_share_2025']:5.1f}%  ({100 * (r['women_share_2025'] - r['women_share_2015']):+.1f})")
print("\nEvery year: women and men in the top fifth, and the implied women's share of messages")
for r in yearly:
    print(f"  {r['year']}  women {100 * r['women_top']:5.2f}%  men {100 * r['men_top']:5.2f}%  implied {100 * r['implied']:5.2f}%  "
          f"(with gender-specific use {100 * r['implied_gender']:5.2f}%)  women's share of employed {100 * r['women_share_employed']:5.2f}%")


# ---------------------------------------------------------------------------
# Figure, written as SVG by hand because matplotlib is not installed.
# ---------------------------------------------------------------------------
WIDTH, HEIGHT, LEFT, RIGHT = 720, 636, 44, 120
PLOT_W = WIDTH - LEFT - RIGHT
A_TOP, A_H, A_LOW, A_HIGH = 112, 200, 10, 35
B_TOP, B_H, B_LOW, B_HIGH = 400, 120, 46, 50
tops = [v for r in yearly for v in (r["women_top"], r["men_top"])]
assert all(A_LOW / 100 <= v <= A_HIGH / 100 for v in tops), "top panel scale"
assert all(B_LOW / 100 <= r["implied"] <= B_HIGH / 100 for r in yearly), "bottom panel scale"


def x_at(k):
    return LEFT + PLOT_W * k / (len(YEARS) - 1)


def y_a(v):
    return A_TOP + A_H * (A_HIGH / 100 - v) / ((A_HIGH - A_LOW) / 100)


def y_b(v):
    return B_TOP + B_H * (B_HIGH / 100 - v) / ((B_HIGH - B_LOW) / 100)


parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="t d" font-family="system-ui, -apple-system, 'Segoe UI', sans-serif">
<title id="t">Women and men in the jobs with the highest ChatGPT use, 2015 to 2025</title>
<desc id="d">Top panel: share of employed women and of employed men who work in the fifth of jobs with the highest ChatGPT use per worker, each year from 2015 to 2025. Bottom panel: the share of work messages that would come from women if each job used ChatGPT as much as today, using each year's employment. All values are in output/06_jobs_2015_2025_yearly.csv.</desc>
<style>
  svg {{ --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#6b6a66; --grid:rgba(11,11,11,.10); --s1:#2a78d6; --s2:#eb6834; --s7:#6250d6; }}
  @media (prefers-color-scheme: dark) {{
    svg {{ --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7; --muted:#a3a29b; --grid:rgba(255,255,255,.10); --s1:#3987e5; --s2:#d95926; --s7:#9085e9; }}
  }}
  text {{ fill:var(--ink2); font-size:13px; }}
  .title {{ fill:var(--ink); font-size:18px; font-weight:600; }}
  .head {{ fill:var(--ink); font-size:14px; font-weight:600; }}
  .small {{ fill:var(--muted); font-size:12px; }}
</style>
<rect width="{WIDTH}" height="{HEIGHT}" fill="var(--surface)"/>
<text x="16" y="30" class="title">A larger share of women now work in the jobs with the highest use</text>
<text x="16" y="52">Norway, 2015 to 2025, with ChatGPT use per job held at today's level</text>
<text x="16" y="86" class="head">Share of employed women and men in the fifth of jobs with the highest use</text>''']


def frame(top, height, low, high, step, y_of, unit):
    v = low
    while v <= high + 1e-9:
        y = y_of(v / 100)
        parts.append(f'<line x1="{LEFT}" x2="{LEFT + PLOT_W}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--grid)"/>')
        parts.append(f'<text x="{LEFT - 8}" y="{y + 4:.1f}" text-anchor="end" class="small">{v:g}{unit}</text>')
        v += step
    for k, y in enumerate(YEARS):
        if int(y) % 2 == 1:
            parts.append(f'<text x="{x_at(k):.1f}" y="{top + height + 18}" text-anchor="middle" class="small">{y}</text>')


def series(values, colour, label, y_of, name):
    pts = " ".join(f"{x_at(k):.1f},{y_of(v):.1f}" for k, v in enumerate(values))
    parts.append(f'<polyline points="{pts}" fill="none" stroke="var({colour})" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
    for k, v in enumerate(values):
        parts.append(f'<circle cx="{x_at(k):.1f}" cy="{y_of(v):.1f}" r="4" fill="var({colour})" stroke="var(--surface)" stroke-width="2">'
                     f'<title>{name}, {YEARS[k]}: {100 * v:.2f} %</title></circle>')
    parts.append(f'<text x="{x_at(len(values) - 1) + 10:.1f}" y="{y_of(values[-1]) + 4:.1f}">{label} {100 * values[-1]:.1f}%</text>')


frame(A_TOP, A_H, A_LOW, A_HIGH, 5, y_a, "%")
series([r["women_top"] for r in yearly], "--s1", "Women", y_a, "Women in the top fifth")
series([r["men_top"] for r in yearly], "--s2", "Men", y_a, "Men in the top fifth")
parts.append(f'<text x="{x_at(0):.1f}" y="{y_a(yearly[0]["women_top"]) + 20:.1f}" class="small">{100 * yearly[0]["women_top"]:.1f}%</text>')
parts.append(f'<text x="{x_at(0):.1f}" y="{y_a(yearly[0]["men_top"]) - 10:.1f}" class="small">{100 * yearly[0]["men_top"]:.1f}%</text>')

parts.append(f'<text x="16" y="{B_TOP - 26}" class="head">Share of work messages from women that the jobs would imply</text>')
frame(B_TOP, B_H, B_LOW, B_HIGH, 1, y_b, "%")
series([r["implied"] for r in yearly], "--s7", "Implied", y_b, "Implied women's share")
parts.append(f'<text x="{x_at(0):.1f}" y="{y_b(yearly[0]["implied"]) - 10:.1f}" class="small">{100 * yearly[0]["implied"]:.1f}%</text>')

parts.append(f'<text x="16" y="{HEIGHT - 62}" class="small">The fifth of jobs with the highest use holds about a fifth of 2025 employment. Use per job comes from job tasks</text>')
parts.append(f'<text x="16" y="{HEIGHT - 44}" class="small">and is held fixed, so this shows where women and men work, not how they use ChatGPT. Code 0000 is excluded.</text>')
parts.append(f'<text x="16" y="{HEIGHT - 26}" class="small">The bottom panel starts at 46 %, so its slope looks steeper than it is. The rise is {100 * (implied["2025"] - implied["2015"]):.1f} points over ten years.</text>')
parts.append(f'<text x="16" y="{HEIGHT - 8}" class="small">Data: ssb_12542_sysselsatte_yrke4_kjonn.csv, styrk08_openai_gender_persons.csv.</text>')
parts.append("</svg>")
(OUT / "06_jobs_2015_2025.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")

print("\nSaved output/06_jobs_2015_2025.csv, _yearly.csv, _groups.csv and output/06_jobs_2015_2025.svg")
