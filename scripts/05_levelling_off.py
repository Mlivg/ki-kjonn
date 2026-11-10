"""Has the rise in women's share of ChatGPT messages levelled off?

Main measure, fixed before the first run: women's share of all messages in
July to September of 2024, 2025 and 2026. The rise from 2024 to 2025 is the
first year. The rise from 2025 to 2026 is the second year. Using the same
calendar months each year keeps seasonal patterns out of the comparison.

Reads only data/raw. Writes to output/.
Uses the Python standard library only. The tests on made-up data run first.
If one fails, the script stops before it reads the real data.

Run from the project folder:
    python3 -I scripts/05_levelling_off.py
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "output"

FOUR = ["Writing", "Practical Guidance", "Seeking information", "Technical help"]
LABEL = {"Writing": "Writing", "Practical Guidance": "Practical guidance",
         "Seeking information": "Seeking information", "Technical help": "Technical help"}


# ---------------------------------------------------------------------------
# The method. Every function takes shares between 0 and 1.
# ---------------------------------------------------------------------------
def window_mean(series, positions):
    """Mean over the window, skipping gaps. Returns the value and the count."""
    values = [series[i] for i in positions if series[i] is not None]
    return (sum(values) / len(values) if values else None), len(values)


def yearly_rises(series, windows):
    """Mean in each window, and the rise from each window to the next."""
    means = [window_mean(series, w)[0] for w in windows]
    rises = [b - a for a, b in zip(means, means[1:])]
    return means, rises


def slope_per_year(points):
    """Least-squares slope of (month number, value) pairs, times 12."""
    n = len(points)
    mx = sum(x for x, _ in points) / n
    my = sum(y for _, y in points) / n
    return 12 * sum((x - mx) * (y - my) for x, y in points) / sum((x - mx) ** 2 for x, _ in points)


def year_on_year(series, i, length=3):
    """Mean of the `length` months ending at i, minus the same months a year earlier."""
    # Python reads a negative position from the end of the list, so stop instead of comparing the wrong months.
    assert i - length - 11 >= 0, "not a full year of data before this month"
    now = window_mean(series, range(i - length + 1, i + 1))[0]
    before = window_mean(series, range(i - length - 11, i - 11))[0]
    return now - before


# ---------------------------------------------------------------------------
# Tests on made-up data, where the right answer is known.
# ---------------------------------------------------------------------------
def close(a, b):
    return abs(a - b) < 1e-9


def run_tests():
    # Rises 10 points a year, then 2: a slowdown by construction.
    series = [0.30] * 3 + [None] * 9 + [0.40] * 3 + [None] * 9 + [0.42] * 3
    means, rises = yearly_rises(series, [[0, 1, 2], [12, 13, 14], [24, 25, 26]])
    assert close(means[1], 0.40) and close(rises[0], 0.10) and close(rises[1], 0.02), "yearly rises"
    assert close(window_mean([0.2, None, 0.4], [0, 1, 2])[0], 0.3), "gap skipped in mean"
    assert window_mean([0.2, None, 0.4], [0, 1, 2])[1] == 2, "gap skipped in count"
    assert close(slope_per_year([(0, 0.30), (6, 0.36), (12, 0.42)]), 0.12), "slope"
    # A straight rise of 1 point a month gives 12 points a year on year.
    line = [0.30 + 0.01 * i for i in range(27)]
    assert close(year_on_year(line, 14), 0.12), "year on year"
    assert close(year_on_year(line, 26), 0.12), "year on year at the end"
    flat = [0.5] * 27
    assert close(year_on_year(flat, 20), 0.0), "year on year, flat"


run_tests()
print("Tests on made-up data passed.\n")


# ---------------------------------------------------------------------------
# Real data.
# ---------------------------------------------------------------------------
with open(RAW / "norway_gender_topics_monthly.csv", newline="", encoding="utf-8") as f:
    monthly = list(csv.DictReader(f))
assert len(monthly) == 27, "expected 27 months"
months = [m["month"][:7] for m in monthly]
assert months[0] == "2024-07" and months[12] == "2025-07" and months[24] == "2026-07", "month positions"
alle = [float(m["Alle"]) for m in monthly]
female = {t: [float(m[t]) if m[t] else None for m in monthly] for t in FOUR}

JUL_SEP = [[0, 1, 2], [12, 13, 14], [24, 25, 26]]
JULY = [[0], [12], [24]]
SEPTEMBER = [[2], [14], [26]]

# The first row is the main result, chosen before any row was run.
versions = [
    ("main", "All messages, July to September each year", alle, JUL_SEP),
    ("july", "All messages, July only", alle, JULY),
    ("september", "All messages, September only", alle, SEPTEMBER),
] + [(f"topic_{t.split()[0].lower()}", f"{LABEL[t]}, July to September each year", female[t], JUL_SEP) for t in FOUR]

rows = []
for name, description, series, windows in versions:
    means, rises = yearly_rises(series, windows)
    counts = [window_mean(series, w)[1] for w in windows]
    rows.append({"spec": name, "description": description,
                 "mean_2024": round(100 * means[0], 2), "mean_2025": round(100 * means[1], 2), "mean_2026": round(100 * means[2], 2),
                 "rise_first_year": round(100 * rises[0], 2), "rise_second_year": round(100 * rises[1], 2),
                 "second_as_share_of_first_pct": round(100 * rises[1] / rises[0], 1),
                 "values_used": "+".join(str(c) for c in counts)})

slope_first = slope_per_year([(i, alle[i]) for i in range(0, 12)])
slope_second = slope_per_year([(i, alle[i]) for i in range(12, 24)])
yoy = [(i, year_on_year(alle, i)) for i in range(14, 27)]

OUT.mkdir(exist_ok=True)
with open(OUT / "05_levelling_off.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
with open(OUT / "05_levelling_off_monthly.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["month", "alle_pct", "three_month_average_pct", "change_from_a_year_earlier_three_month_average"])
    yoy_by_month = dict(yoy)
    for i in range(27):
        avg = window_mean(alle, range(i - 2, i + 1))[0] if i >= 2 else None
        w.writerow([months[i], round(100 * alle[i], 2), "" if avg is None else round(100 * avg, 2),
                    round(100 * yoy_by_month[i], 2) if i in yoy_by_month else ""])

print(f"{'spec':22} {'2024':>6} {'2025':>6} {'2026':>6} {'year 1':>7} {'year 2':>7} {'2 / 1':>7}  values used")
for r in rows:
    print(f"{r['spec']:22} {r['mean_2024']:6.2f} {r['mean_2025']:6.2f} {r['mean_2026']:6.2f} {r['rise_first_year']:+7.2f} "
          f"{r['rise_second_year']:+7.2f} {r['second_as_share_of_first_pct']:6.1f}%  {r['values_used']}")
print(f"\nStraight-line trend, July 2024 to June 2025: {100 * slope_first:+.2f} points per year")
print(f"Straight-line trend, July 2025 to June 2026: {100 * slope_second:+.2f} points per year")
print("\nChange from a year earlier, 3-month averages ending in each month, in points")
for i, v in yoy:
    print(f"  {months[i]}  {100 * v:+.2f}")


# ---------------------------------------------------------------------------
# Figure, written as SVG by hand because matplotlib is not installed.
# ---------------------------------------------------------------------------
WIDTH, HEIGHT, LEFT, RIGHT = 720, 658, 44, 60
PLOT_W = WIDTH - LEFT - RIGHT
A_TOP, A_H, A_LOW, A_HIGH = 104, 230, 30, 60
B_TOP, B_H, B_LOW, B_HIGH = 418, 130, -2, 12
avg3 = [window_mean(alle, range(i - 2, i + 1))[0] if i >= 2 else None for i in range(27)]
assert all(A_LOW / 100 <= v <= A_HIGH / 100 for v in alle), "top panel scale"
assert all(B_LOW <= 100 * v <= B_HIGH for _, v in yoy), "bottom panel scale"


def x_at(i):
    return LEFT + PLOT_W * i / 26


def y_a(v):
    return A_TOP + A_H * (A_HIGH / 100 - v) / ((A_HIGH - A_LOW) / 100)


def y_b(points):
    return B_TOP + B_H * (B_HIGH - points) / (B_HIGH - B_LOW)


parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="t d" font-family="system-ui, -apple-system, 'Segoe UI', sans-serif">
<title id="t">Women's share of ChatGPT messages in Norway, and how much it rose from a year earlier</title>
<desc id="d">Top panel: women's share of all messages per month, July 2024 to September 2026, with a 3-month average. Shaded bands mark July to September each year. Bottom panel: the 3-month average minus the same months a year earlier. All values are in output/05_levelling_off.csv and output/05_levelling_off_monthly.csv.</desc>
<style>
  svg {{ --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#6b6a66; --grid:rgba(11,11,11,.10); --axis:rgba(11,11,11,.45); --band:rgba(11,11,11,.05); --s1:#2a78d6; }}
  @media (prefers-color-scheme: dark) {{
    svg {{ --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7; --muted:#a3a29b; --grid:rgba(255,255,255,.10); --axis:rgba(255,255,255,.45); --band:rgba(255,255,255,.06); --s1:#3987e5; }}
  }}
  text {{ fill:var(--ink2); font-size:13px; }}
  .title {{ fill:var(--ink); font-size:18px; font-weight:600; }}
  .head {{ fill:var(--ink); font-size:14px; font-weight:600; }}
  .small {{ fill:var(--muted); font-size:12px; }}
  .value {{ fill:var(--ink); font-size:12px; font-weight:600; }}
</style>
<rect width="{WIDTH}" height="{HEIGHT}" fill="var(--surface)"/>
<text x="16" y="30" class="title">The rise slowed in the second year</text>
<text x="16" y="52">Women's share of ChatGPT messages in Norway, July 2024 to September 2026</text>
<text x="16" y="86" class="head">Share of all messages from women</text>''']


def month_labels(top):
    for i, m in enumerate(months):
        if m[5:7] in ("01", "07"):
            label = {"01": "Jan", "07": "Jul"}[m[5:7]] + " " + m[:4]
            anchor = "start" if i == 0 else "middle"
            parts.append(f'<text x="{x_at(i):.1f}" y="{top}" text-anchor="{anchor}" class="small">{label}</text>')


# Top panel: July to September bands, gridlines, monthly values and the 3-month average.
step = PLOT_W / 26
for w in JUL_SEP:
    x0 = max(LEFT, x_at(w[0]) - step / 2)
    x1 = min(LEFT + PLOT_W, x_at(w[-1]) + step / 2)
    parts.append(f'<rect x="{x0:.1f}" y="{A_TOP}" width="{x1 - x0:.1f}" height="{A_H}" fill="var(--band)"/>')
for tick in range(A_LOW, A_HIGH + 1, 10):
    y = y_a(tick / 100)
    parts.append(f'<line x1="{LEFT}" x2="{LEFT + PLOT_W}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--grid)"/>')
    parts.append(f'<text x="{LEFT - 8}" y="{y + 4:.1f}" text-anchor="end" class="small">{tick}%</text>')
month_labels(A_TOP + A_H + 18)
pts = " ".join(f"{x_at(i):.1f},{y_a(v):.1f}" for i, v in enumerate(alle))
parts.append(f'<polyline points="{pts}" fill="none" stroke="var(--muted)" stroke-width="1.5" stroke-linejoin="round"/>')
pts = " ".join(f"{x_at(i):.1f},{y_a(v):.1f}" for i, v in enumerate(avg3) if v is not None)
parts.append(f'<polyline points="{pts}" fill="none" stroke="var(--s1)" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
for w, key in zip(JUL_SEP, ("mean_2024", "mean_2025", "mean_2026")):
    xm = x_at(w[1])
    value = rows[0][key]
    parts.append(f'<text x="{xm:.1f}" y="{A_TOP + 16}" text-anchor="middle" class="value">{value:.1f}%</text>')
parts.append(f'<line x1="{LEFT + 150}" x2="{LEFT + 166}" y1="{A_TOP + A_H - 14}" y2="{A_TOP + A_H - 14}" stroke="var(--muted)" stroke-width="1.5"/>')
parts.append(f'<text x="{LEFT + 171}" y="{A_TOP + A_H - 10}" class="small">Each month</text>')
parts.append(f'<line x1="{LEFT + 260}" x2="{LEFT + 276}" y1="{A_TOP + A_H - 14}" y2="{A_TOP + A_H - 14}" stroke="var(--s1)" stroke-width="2.5"/>')
parts.append(f'<text x="{LEFT + 281}" y="{A_TOP + A_H - 10}" class="small">3-month average</text>')

# Bottom panel: change from a year earlier.
parts.append(f'<text x="16" y="{B_TOP - 26}" class="head">Change from a year earlier, 3-month average, in percentage points</text>')
for tick in range(0, B_HIGH + 1, 4):
    y = y_b(tick)
    parts.append(f'<line x1="{LEFT}" x2="{LEFT + PLOT_W}" y1="{y:.1f}" y2="{y:.1f}" stroke="var({"--axis" if tick == 0 else "--grid"})"/>')
    parts.append(f'<text x="{LEFT - 8}" y="{y + 4:.1f}" text-anchor="end" class="small">{tick}</text>')
month_labels(B_TOP + B_H + 18)
pts = " ".join(f"{x_at(i):.1f},{y_b(100 * v):.1f}" for i, v in yoy)
parts.append(f'<polyline points="{pts}" fill="none" stroke="var(--s1)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
for i, v in yoy:
    parts.append(f'<circle cx="{x_at(i):.1f}" cy="{y_b(100 * v):.1f}" r="4" fill="var(--s1)" stroke="var(--surface)" stroke-width="2">'
                 f'<title>{months[i]}: {100 * v:+.1f} points</title></circle>')
for i, v in (yoy[0], yoy[-1]):
    parts.append(f'<text x="{x_at(i) + 8:.1f}" y="{y_b(100 * v) - 8:.1f}" class="value">{100 * v:+.1f}</text>')

parts.append(f'<text x="16" y="{HEIGHT - 44}" class="small">Shaded: July to September each year, with their averages. Each 3-month average ends in the month shown.</text>')
parts.append(f'<text x="16" y="{HEIGHT - 26}" class="small">The bottom panel starts in September 2025, the first month with a full year of data before it.</text>')
parts.append(f'<text x="16" y="{HEIGHT - 8}" class="small">Data: norway_gender_topics_monthly.csv, column Alle.</text>')
parts.append("</svg>")
(OUT / "05_levelling_off.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")

print("\nSaved output/05_levelling_off.csv, output/05_levelling_off_monthly.csv and output/05_levelling_off.svg")
