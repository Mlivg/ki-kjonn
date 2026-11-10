"""Are the gaps between topics closing?

Women's share of ChatGPT messages differs a lot between topics. This script
measures whether those differences got smaller from July 2024 to September 2026.

Main measure, fixed before the first run: the gap between the topic with the
highest and the lowest women's share, among the four topics with values in the
first three months, comparing the first and last 3 months.

Reads only data/raw. Writes to output/.
Uses the Python standard library only. The tests on made-up data run first.
If one fails, the script stops before it reads the real data.

Run from the project folder:
    python3 -I scripts/04_topic_gaps.py
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "output"

FOUR = ["Writing", "Practical Guidance", "Seeking information", "Technical help"]
SEVEN = FOUR + ["Multimedia", "Self-expression", "Other/Unknown"]
LABEL = {"Writing": "Writing", "Practical Guidance": "Practical guidance",
         "Seeking information": "Seeking information", "Technical help": "Technical help",
         "Multimedia": "Multimedia", "Self-expression": "Self-expression", "Other/Unknown": "Other/unknown"}


# ---------------------------------------------------------------------------
# The method. Every function takes shares between 0 and 1.
# ---------------------------------------------------------------------------
def window_mean(series, positions):
    """Mean over the window, skipping gaps. Returns the value and the count."""
    values = [series[i] for i in positions if series[i] is not None]
    return (sum(values) / len(values) if values else None), len(values)


def spread(shares):
    """Highest minus lowest share, and which topics they are."""
    high = max(shares, key=shares.get)
    low = min(shares, key=shares.get)
    return shares[high] - shares[low], high, low


def mean_distance_from_half(shares):
    """Average distance from 50 %, ignoring direction."""
    return sum(abs(v - 0.5) for v in shares.values()) / len(shares)


def slope_per_year(points):
    """Least-squares slope of (month number, value) pairs, times 12."""
    n = len(points)
    mx = sum(x for x, _ in points) / n
    my = sum(y for _, y in points) / n
    return 12 * sum((x - mx) * (y - my) for x, y in points) / sum((x - mx) ** 2 for x, _ in points)


# ---------------------------------------------------------------------------
# Tests on made-up data, where the right answer is known.
# ---------------------------------------------------------------------------
def close(a, b):
    return abs(a - b) < 1e-9


def run_tests():
    gap, high, low = spread({"A": 0.6, "B": 0.2, "C": 0.45})
    assert close(gap, 0.4) and high == "A" and low == "B", "spread"
    assert close(mean_distance_from_half({"A": 0.6, "B": 0.2, "C": 0.45}), (0.1 + 0.3 + 0.05) / 3), "distance from half"
    assert close(window_mean([0.2, None, 0.4], [0, 1, 2])[0], 0.3), "gap skipped in mean"
    assert window_mean([0.2, None, 0.4], [0, 1, 2])[1] == 2, "gap skipped in count"
    assert window_mean([None, None], [0, 1]) == (None, 0), "empty window"
    assert close(slope_per_year([(0, 0.30), (6, 0.27), (12, 0.24)]), -0.06), "slope"
    assert close(slope_per_year([(0, 0.1), (1, 0.3), (2, 0.2)]), 12 * 0.05), "slope with noise"


run_tests()
print("Tests on made-up data passed.\n")


# ---------------------------------------------------------------------------
# Real data.
# ---------------------------------------------------------------------------
with open(RAW / "norway_gender_topics_monthly.csv", newline="", encoding="utf-8") as f:
    monthly = list(csv.DictReader(f))
assert len(monthly) == 27, "expected 27 months"
months = [m["month"][:7] for m in monthly]
female = {t: [float(m[t]) if m[t] else None for m in monthly] for t in SEVEN}
alle = [float(m["Alle"]) for m in monthly]
complete = [i for i in range(27) if all(female[t][i] is not None for t in FOUR)]


def first(n):
    return list(range(n))


def last(n):
    return list(range(27 - n, 27))


def run(name, description, topics, start, end):
    s0, s1, n0, n1 = {}, {}, {}, {}
    for t in topics:
        s0[t], n0[t] = window_mean(female[t], start)
        s1[t], n1[t] = window_mean(female[t], end)
        assert s0[t] is not None and s1[t] is not None, f"{name}: {t} has no value in a window"
    gap0, high0, low0 = spread(s0)
    gap1, high1, low1 = spread(s1)
    return {
        "name": name, "description": description, "topics": topics, "start": start, "end": end,
        "s0": s0, "s1": s1, "n0": n0, "n1": n1,
        "alle0": sum(alle[i] for i in start) / len(start), "alle1": sum(alle[i] for i in end) / len(end),
        "gap0": gap0, "gap1": gap1, "high0": high0, "low0": low0, "high1": high1, "low1": low1,
        "dist0": mean_distance_from_half(s0), "dist1": mean_distance_from_half(s1),
    }


# The first row is the main result, chosen before any row was run.
runs = [
    run("main", "Four topics, first and last 3 months", FOUR, first(3), last(3)),
    run("six_months", "Four topics, first and last 6 months", FOUR, first(6), last(6)),
    run("twelve_months", "Four topics, first and last 12 months", FOUR, first(12), last(12)),
    run("complete_months", "Four topics, first and last 3 months with all four published", FOUR, complete[:3], complete[-3:]),
    run("seven_twelve_months", "All seven topics, first and last 12 months", SEVEN, first(12), last(12)),
]
main = runs[0]

# Month by month, in the months where all four topics are published.
monthly_gap = [(i, spread({t: female[t][i] for t in FOUR})) for i in complete]
trend = slope_per_year([(i, g) for i, (g, _, _) in monthly_gap])
highest_counts = {t: sum(1 for _, (_, h, _) in monthly_gap if h == t) for t in FOUR}
lowest_counts = {t: sum(1 for _, (_, _, l) in monthly_gap if l == t) for t in FOUR}

OUT.mkdir(exist_ok=True)
with open(OUT / "04_topic_gaps.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["spec", "description", "start_months", "end_months", "gap_start", "gap_end", "gap_change",
                "highest_start", "lowest_start", "highest_end", "lowest_end",
                "mean_distance_from_50_start", "mean_distance_from_50_end", "mean_distance_change"])
    for r in runs:
        w.writerow([r["name"], r["description"], " ".join(months[i] for i in r["start"]), " ".join(months[i] for i in r["end"]),
                    round(100 * r["gap0"], 2), round(100 * r["gap1"], 2), round(100 * (r["gap1"] - r["gap0"]), 2),
                    LABEL[r["high0"]], LABEL[r["low0"]], LABEL[r["high1"]], LABEL[r["low1"]],
                    round(100 * r["dist0"], 2), round(100 * r["dist1"], 2), round(100 * (r["dist1"] - r["dist0"]), 2)])

with open(OUT / "04_topic_gaps_topics.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["topic", "female_start_pct", "female_end_pct", "change", "distance_from_50_start", "distance_from_50_end",
                "minus_total_start", "minus_total_end", "start_values_used", "end_values_used"])
    for t in FOUR:
        w.writerow([LABEL[t], round(100 * main["s0"][t], 2), round(100 * main["s1"][t], 2),
                    round(100 * (main["s1"][t] - main["s0"][t]), 2),
                    round(100 * (main["s0"][t] - 0.5), 2), round(100 * (main["s1"][t] - 0.5), 2),
                    round(100 * (main["s0"][t] - main["alle0"]), 2), round(100 * (main["s1"][t] - main["alle1"]), 2),
                    main["n0"][t], main["n1"][t]])

print(f"{'spec':20} {'gap start':>9} {'gap end':>8} {'change':>7} {'dist50 start':>12} {'dist50 end':>10}  highest/lowest at start -> end")
for r in runs:
    print(f"{r['name']:20} {100 * r['gap0']:9.2f} {100 * r['gap1']:8.2f} {100 * (r['gap1'] - r['gap0']):+7.2f} "
          f"{100 * r['dist0']:12.2f} {100 * r['dist1']:10.2f}  {LABEL[r['high0']]}/{LABEL[r['low0']]} -> {LABEL[r['high1']]}/{LABEL[r['low1']]}")

print("\nMain result, by topic")
for t in FOUR:
    print(f"  {LABEL[t]:20} {100 * main['s0'][t]:5.1f} ({main['n0'][t]}) -> {100 * main['s1'][t]:5.1f} ({main['n1'][t]})  "
          f"from 50 %: {100 * (main['s0'][t] - 0.5):+6.1f} -> {100 * (main['s1'][t] - 0.5):+6.1f}  "
          f"from total: {100 * (main['s0'][t] - main['alle0']):+6.1f} -> {100 * (main['s1'][t] - main['alle1']):+6.1f}")

print(f"\nMonth by month, {len(monthly_gap)} months with all four topics")
print(f"  gap: first {100 * monthly_gap[0][1][0]:.1f} ({months[monthly_gap[0][0]]}), last {100 * monthly_gap[-1][1][0]:.1f} ({months[monthly_gap[-1][0]]}), "
      f"lowest {100 * min(g for _, (g, _, _) in monthly_gap):.1f}, highest {100 * max(g for _, (g, _, _) in monthly_gap):.1f}")
print(f"  straight-line trend: {100 * trend:+.2f} points per year")
print(f"  months each topic is highest: { {LABEL[t]: n for t, n in highest_counts.items()} }")
print(f"  months each topic is lowest:  { {LABEL[t]: n for t, n in lowest_counts.items()} }")


# ---------------------------------------------------------------------------
# Figure, written as SVG by hand because matplotlib is not installed.
# ---------------------------------------------------------------------------
WIDTH, HEIGHT, LEFT, RIGHT = 720, 438, 44, 40
TOP, PLOT_H, LOW, HIGH = 104, 220, 0, 40
PLOT_W = WIDTH - LEFT - RIGHT
assert all(LOW / 100 <= g <= HIGH / 100 for _, (g, _, _) in monthly_gap), "figure scale"


def x_at(i):
    return LEFT + PLOT_W * i / 26


def y_at(v):
    return TOP + PLOT_H * (HIGH / 100 - v) / ((HIGH - LOW) / 100)


parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="t d" font-family="system-ui, -apple-system, 'Segoe UI', sans-serif">
<title id="t">Gap between the topics with the highest and lowest women's share, by month</title>
<desc id="d">For each month where writing, practical guidance, seeking information and technical help are all published, the highest women's share minus the lowest. July 2024 to September 2026. All values are in output/04_topic_gaps.csv and data/raw/norway_gender_topics_monthly.csv.</desc>
<style>
  svg {{ --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#6b6a66; --grid:rgba(11,11,11,.10); --s1:#2a78d6; }}
  @media (prefers-color-scheme: dark) {{
    svg {{ --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7; --muted:#a3a29b; --grid:rgba(255,255,255,.10); --s1:#3987e5; }}
  }}
  text {{ fill:var(--ink2); font-size:13px; }}
  .title {{ fill:var(--ink); font-size:18px; font-weight:600; }}
  .small {{ fill:var(--muted); font-size:12px; }}
  .value {{ fill:var(--ink); font-size:12px; font-weight:600; }}
</style>
<rect width="{WIDTH}" height="{HEIGHT}" fill="var(--surface)"/>
<text x="16" y="30" class="title">The gap between topics shrank, with large swings month to month</text>
<text x="16" y="52">Highest minus lowest women's share among four topics, in percentage points, per month</text>''']

for tick in range(LOW, HIGH + 1, 10):
    y = y_at(tick / 100)
    parts.append(f'<line x1="{LEFT}" x2="{LEFT + PLOT_W}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--grid)"/>')
    parts.append(f'<text x="{LEFT - 8}" y="{y + 4:.1f}" text-anchor="end" class="small">{tick}</text>')
for i, m in enumerate(months):
    if m[5:7] in ("01", "07"):
        label = {"01": "Jan", "07": "Jul"}[m[5:7]] + " " + m[:4]
        anchor = "start" if i == 0 else "middle"
        parts.append(f'<text x="{x_at(i):.1f}" y="{TOP + PLOT_H + 18}" text-anchor="{anchor}" class="small">{label}</text>')

# Straight-line trend through the monthly values, drawn as a thin muted line.
xs = [i for i, _ in monthly_gap]
mean_x = sum(xs) / len(xs)
mean_y = sum(g for _, (g, _, _) in monthly_gap) / len(monthly_gap)
trend_at = lambda i: mean_y + trend / 12 * (i - mean_x)
parts.append(f'<line x1="{x_at(xs[0]):.1f}" y1="{y_at(trend_at(xs[0])):.1f}" x2="{x_at(xs[-1]):.1f}" y2="{y_at(trend_at(xs[-1])):.1f}" '
             'stroke="var(--muted)" stroke-width="1.5"/>')
parts.append(f'<text x="{x_at(xs[-1]) - 6:.1f}" y="{y_at(trend_at(xs[-1])) + 22:.1f}" text-anchor="end" class="small">'
             f'Trend {100 * trend:+.1f} points per year</text>')

# A month without all four topics breaks the line.
run_points = []
for k, (i, (g, high, low)) in enumerate(monthly_gap):
    run_points.append((i, g))
    next_i = monthly_gap[k + 1][0] if k + 1 < len(monthly_gap) else None
    if next_i != i + 1:
        if len(run_points) > 1:
            pts = " ".join(f"{x_at(a):.1f},{y_at(b):.1f}" for a, b in run_points)
            parts.append(f'<polyline points="{pts}" fill="none" stroke="var(--s1)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
        run_points = []
for i, (g, high, low) in monthly_gap:
    parts.append(f'<circle cx="{x_at(i):.1f}" cy="{y_at(g):.1f}" r="4" fill="var(--s1)" stroke="var(--surface)" stroke-width="2">'
                 f'<title>{months[i]}: {100 * g:.1f} points ({LABEL[high]} highest, {LABEL[low]} lowest)</title></circle>')
first_i, (first_g, _, _) = monthly_gap[0]
last_i, (last_g, _, _) = monthly_gap[-1]
parts.append(f'<text x="{x_at(first_i):.1f}" y="{y_at(first_g) - 10:.1f}" class="value">{100 * first_g:.1f}</text>')
parts.append(f'<text x="{x_at(last_i):.1f}" y="{y_at(last_g) - 10:.1f}" text-anchor="middle" class="value">{100 * last_g:.1f}</text>')

parts.append(f'<text x="16" y="{HEIGHT - 62}" class="small">Topics: writing, practical guidance, seeking information, technical help. A break is a month where</text>')
parts.append(f'<text x="16" y="{HEIGHT - 44}" class="small">OpenAI withheld at least one of them. It does not publish a value based on fewer than 100 messages,</text>')
# The footnote states which topics are the extremes, so check that it is true for every month shown.
assert highest_counts["Writing"] == lowest_counts["Technical help"] == len(monthly_gap), "footnote no longer true"
parts.append(f'<text x="16" y="{HEIGHT - 26}" class="small">to protect privacy. Writing is highest and technical help lowest in every month shown.</text>')
parts.append(f'<text x="16" y="{HEIGHT - 8}" class="small">Data: norway_gender_topics_monthly.csv.</text>')
parts.append("</svg>")
(OUT / "04_topic_gaps.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")

print("\nSaved output/04_topic_gaps.csv, output/04_topic_gaps_topics.csv and output/04_topic_gaps.svg")
