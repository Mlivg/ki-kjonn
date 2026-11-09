"""Split the rise in women's share of ChatGPT messages using the measured topic mix.

Analysis 02 did not have each topic's share of messages per month, so the mix
effect was only what remained. OpenAI's download has that share for Norway.
This script measures both parts:

  within = sum over topics of (average topic share) x (change in women's share)
  mix    = sum over topics of (average women's share) x (change in topic share)

Using averages of the start and end periods means the two parts add up to the
change in the rebuilt total, with no separate interaction term. Any difference
from the published total is reported as unexplained.

Reads only data/raw and data/raw_openai_signals. Writes to output/.
Uses the Python standard library only. The tests on made-up data run first.
If one fails, the script stops before it reads the real data.

Run from the project folder:
    python3 -I scripts/03_measured_mix.py
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OPENAI = ROOT / "data" / "raw_openai_signals"
OUT = ROOT / "output"

FOUR = ["Writing", "Practical Guidance", "Seeking information", "Technical help"]
# These three lack a value in at least two of the first three months.
THIN_START = ["Multimedia", "Self-expression", "Other/Unknown"]
SEVEN = FOUR + THIN_START


# ---------------------------------------------------------------------------
# The method. Every function takes shares between 0 and 1.
# ---------------------------------------------------------------------------
def normalise(shares):
    """Rescale shares so they sum to exactly 1. Rounding leaves them near 1."""
    total = sum(shares.values())
    return {t: v / total for t, v in shares.items()}


def fill_gaps(series, nearest_at_ends=False):
    """Fill gaps on a straight line. End gaps stay empty unless asked for."""
    known = [i for i, v in enumerate(series) if v is not None]
    filled = list(series)
    for i, v in enumerate(series):
        if v is not None:
            continue
        before = [k for k in known if k < i]
        after = [k for k in known if k > i]
        if before and after:
            a, b = before[-1], after[0]
            filled[i] = series[a] + (series[b] - series[a]) * (i - a) / (b - a)
        elif nearest_at_ends and (before or after):
            filled[i] = series[before[-1]] if before else series[after[0]]
    return filled


def window_value(series, positions):
    """Mean over the window, skipping gaps.

    If the window has no value, use the published value nearest to the window.
    Returns the value and how many values in the window were used.
    """
    values = [series[i] for i in positions if series[i] is not None]
    if values:
        return sum(values) / len(values), len(values)
    known = [i for i, v in enumerate(series) if v is not None]
    nearest = min(known, key=lambda k: min(abs(k - p) for p in positions))
    return series[nearest], 0


def split(f0, f1, w0, w1):
    """Split the change in the sum of weight x share into two parts, by topic.

    The topic's mix part uses its distance from the average total. This does
    not change the sum, because the changes in weights sum to zero. It shows the
    right direction: a low-share topic that shrinks pushes women's share up.
    """
    average_total = (sum(w0[t] * f0[t] for t in f0) + sum(w1[t] * f1[t] for t in f0)) / 2
    within = {t: (w0[t] + w1[t]) / 2 * (f1[t] - f0[t]) for t in f0}
    mix = {t: ((f0[t] + f1[t]) / 2 - average_total) * (w1[t] - w0[t]) for t in f0}
    return within, mix


# ---------------------------------------------------------------------------
# Tests on made-up data, where the right answer is known.
# ---------------------------------------------------------------------------
def close(a, b):
    return abs(a - b) < 1e-9


def run_tests():
    # Unequal rises. By hand: within 11.75 points, mix 11.25 points, total 23 points.
    w0 = {"A": 0.2, "B": 0.3, "C": 0.5}
    w1 = {"A": 0.5, "B": 0.3, "C": 0.2}
    f0 = {"A": 0.5, "B": 0.3, "C": 0.2}
    f1 = {"A": 0.7, "B": 0.4, "C": 0.25}
    within, mix = split(f0, f1, w0, w1)
    assert close(sum(within.values()), 0.1175), "within part"
    assert close(sum(mix.values()), 0.1125), "mix part"
    start = sum(w0[t] * f0[t] for t in f0)
    end = sum(w1[t] * f1[t] for t in f0)
    assert close(start, 0.29) and close(end, 0.52), "levels"
    assert close(sum(within.values()) + sum(mix.values()), end - start), "the parts add up"
    # By hand for C: (0.225 - 0.405) x -0.3 = +0.054. A low-share topic shrinks, so this is positive.
    assert close(mix["C"], 0.054), "direction of a topic's mix part"

    # Only the mix moves.
    within, mix = split(f0, f0, w0, w1)
    assert close(sum(within.values()), 0.0), "pure mix: within part"
    assert close(sum(mix.values()), 0.09), "pure mix: mix part"

    # Only the shares within topics move.
    within, mix = split(f0, f1, w0, w0)
    assert close(sum(mix.values()), 0.0), "pure within: mix part"
    assert close(sum(within.values()), 0.2 * 0.2 + 0.3 * 0.1 + 0.5 * 0.05), "pure within: within part"

    # Rescaling.
    assert close(normalise({"A": 0.5, "B": 0.501})["A"], 0.5 / 1.001), "normalise"

    # Windows and gaps.
    assert close(window_value([0.2, None, 0.4, 0.9], [0, 1, 2])[0], 0.3), "gap skipped in mean"
    assert window_value([0.2, None, 0.4, 0.9], [0, 1, 2])[1] == 2, "gap skipped in count"
    assert window_value([None, None, 0.5, 0.9], [0, 1]) == (0.5, 0), "nearest value after window"
    assert window_value([0.3, 0.5, None, None], [2, 3]) == (0.5, 0), "nearest value before window"
    assert close(fill_gaps([0.1, None, None, 0.4])[1], 0.2), "straight line"
    assert fill_gaps([None, 0.1])[0] is None, "start stays empty"
    assert fill_gaps([None, 0.1], nearest_at_ends=True)[0] == 0.1, "nearest value"


run_tests()
print("Tests on made-up data passed.\n")


# ---------------------------------------------------------------------------
# Real data.
# ---------------------------------------------------------------------------
def read(folder, name):
    with open(folder / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


monthly = read(RAW, "norway_gender_topics_monthly.csv")
assert len(monthly) == 27, "expected 27 months"
month_days = [m["month"] for m in monthly]
months = [d[:7] for d in month_days]
female = {t: [float(m[t]) if m[t] else None for m in monthly] for t in SEVEN}
alle = [float(m["Alle"]) for m in monthly]


def read_mix(name, **condition):
    """Norway's topic mix per month, rescaled to sum to 1 in each month."""
    rows = [r for r in read(OPENAI, name) if r["country"] == "NO"
            and all(r[k] == v for k, v in condition.items())]
    table = {(r["month"], r["topic"]): r["share_of_messages"] for r in rows}
    assert len(table) == 27 * 7, f"{name}: expected 27 months x 7 topics"
    assert all(table.values()), f"{name}: empty cell"
    return [normalise({t: float(table[(d, t)]) for t in SEVEN}) for d in month_days]


mix_all = read_mix("share_of_messages_by_topic_country_month.csv")
mix_work = read_mix("share_of_messages_by_topic_work_related_country_month.csv", work_related="1")

# The kiindeksen file must equal OpenAI's own numbers for feminine names.
openai_gender = [r for r in read(OPENAI, "share_of_messages_by_gender_topic_country_month.csv")
                 if r["country"] == "NO" and r["typical_name_gender"] == "feminine"]
assert {(r["month"], r["topic"]): float(r["share_of_messages"]) for r in openai_gender} == {
    (d, t): female[t][i] for i, d in enumerate(month_days) for t in SEVEN if female[t][i] is not None
}, "female shares differ between the two sources"
openai_total = {r["month"]: float(r["share_of_messages"])
                for r in read(OPENAI, "share_of_messages_by_gender_country_month.csv")
                if r["country"] == "NO" and r["typical_name_gender"] == "feminine"}
assert openai_total == dict(zip(month_days, alle)), "the total differs between the two sources"


# ---------------------------------------------------------------------------
# Step 1: do the files fit together? Rebuild the total where all topics exist.
# ---------------------------------------------------------------------------
FIT_LIMIT = 0.01  # Set before the first run: mean absolute difference of at most 1 point.
complete = [i for i in range(27) if all(female[t][i] is not None for t in SEVEN)]
fit = [(months[i], sum(mix_all[i][t] * female[t][i] for t in SEVEN), alle[i]) for i in complete]
fit_diffs = [rebuilt - total for _, rebuilt, total in fit]
fit_mean_abs = sum(abs(d) for d in fit_diffs) / len(fit_diffs)
fit_mean = sum(fit_diffs) / len(fit_diffs)

print(f"Fit check: the total rebuilt from topics, in the {len(fit)} months with all seven topics")
for month, rebuilt, total in fit:
    print(f"  {month}  rebuilt={100 * rebuilt:6.2f}  published={100 * total:6.2f}  difference={100 * (rebuilt - total):+5.2f}")
print(f"  mean difference {100 * fit_mean:+.2f}, mean absolute difference {100 * fit_mean_abs:.2f} points, limit {100 * FIT_LIMIT:.2f}")
assert fit_mean_abs <= FIT_LIMIT, "the files do not fit together closely enough"
print("  Within the limit.\n")


# ---------------------------------------------------------------------------
# Step 2: the split, in one main version and several tests.
# ---------------------------------------------------------------------------
def first(n):
    return list(range(n))


def last(n):
    return list(range(27 - n, 27))


def run(name, description, start, end, topics=SEVEN, mixes=mix_all, shares=female, change_start=None):
    """Run one version. change_start replaces start shares for the what-if tests."""
    f0, f1, n0, n1 = {}, {}, {}, {}
    for t in topics:
        f0[t], n0[t] = window_value(shares[t], start)
        f1[t], n1[t] = window_value(shares[t], end)
    if change_start:
        f0 = {t: change_start(t, v) for t, v in f0.items()}
    w0 = normalise({t: sum(mixes[i][t] for i in start) / len(start) for t in topics})
    w1 = normalise({t: sum(mixes[i][t] for i in end) / len(end) for t in topics})
    within, mix = split(f0, f1, w0, w1)
    total_start = sum(alle[i] for i in start) / len(start)
    total_end = sum(alle[i] for i in end) / len(end)
    actual = total_end - total_start
    return {
        "name": name, "description": description, "start": start, "end": end,
        "f0": f0, "f1": f1, "n0": n0, "n1": n1, "w0": w0, "w1": w1,
        "by_topic_within": within, "by_topic_mix": mix,
        "within": sum(within.values()), "mix": sum(mix.values()),
        "total_start": total_start, "total_end": total_end, "actual": actual,
        "rebuilt_start": sum(w0[t] * f0[t] for t in topics),
        "rebuilt_end": sum(w1[t] * f1[t] for t in topics),
        "unexplained": actual - sum(within.values()) - sum(mix.values()),
    }


def shift_thin(points):
    """What-if: the three thin topics started this many points away from the main value."""
    return lambda t, v: min(1.0, max(0.0, v + points / 100)) if t in THIN_START else v


def set_thin(level):
    """What-if: the three thin topics started at exactly this share."""
    return lambda t, v: level if t in THIN_START else v


filled = {t: fill_gaps(female[t], nearest_at_ends=True) for t in SEVEN}

# Does the rebuilt total drift away from the published total over time? This uses
# filled gaps, so it is weaker evidence than the fit check above.
drift = [100 * (sum(mix_all[i][t] * filled[t][i] for t in SEVEN) - alle[i]) for i in range(27)]
print("Rebuilt minus published total, all months, gaps filled, in points")
for label, part in (("first 9 months", drift[:9]), ("middle 9 months", drift[9:18]), ("last 9 months", drift[18:])):
    print(f"  {label:16} mean {sum(part) / 9:+.2f}")
print()

# The first row is the main result, chosen before any row was run.
runs = [
    run("main", "All seven topics, first and last 3 months, nearest value for empty windows", first(3), last(3)),
    run("six_months", "First and last 6 months", first(6), last(6)),
    run("twelve_months", "First and last 12 months", first(12), last(12)),
    run("single_months", "July 2024 against September 2026", first(1), last(1)),
    run("four_topics", "Only the four topics with early values, mix rescaled to them", first(3), last(3), topics=FOUR),
    run("gaps_filled", "Same as main, gaps filled on a straight line first", first(3), last(3), shares=filled),
    run("thin_minus_20", "Thin topics start 20 points lower", first(3), last(3), change_start=shift_thin(-20)),
    run("thin_minus_10", "Thin topics start 10 points lower", first(3), last(3), change_start=shift_thin(-10)),
    run("thin_plus_10", "Thin topics start 10 points higher", first(3), last(3), change_start=shift_thin(10)),
    run("thin_at_0", "Extreme: thin topics start at 0 %", first(3), last(3), change_start=set_thin(0.0)),
    run("thin_at_100", "Extreme: thin topics start at 100 %", first(3), last(3), change_start=set_thin(1.0)),
    run("work_mix", "Topic mix of work messages, compared with analysis 02", first(3), last(3), mixes=mix_work),
]

OUT.mkdir(exist_ok=True)
with open(OUT / "03_measured_mix.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["spec", "description", "start_months", "end_months", "alle_start_pct", "alle_end_pct",
                     "rebuilt_start_pct", "rebuilt_end_pct", "actual_rise", "within", "mix", "unexplained",
                     "within_share_of_rise_pct", "mix_share_of_rise_pct"])
    for r in runs:
        writer.writerow([r["name"], r["description"], " ".join(months[i] for i in r["start"]),
                         " ".join(months[i] for i in r["end"]),
                         round(100 * r["total_start"], 2), round(100 * r["total_end"], 2),
                         round(100 * r["rebuilt_start"], 2), round(100 * r["rebuilt_end"], 2),
                         round(100 * r["actual"], 2), round(100 * r["within"], 2), round(100 * r["mix"], 2),
                         round(100 * r["unexplained"], 2), round(100 * r["within"] / r["actual"], 1),
                         round(100 * r["mix"] / r["actual"], 1)])

main = runs[0]
with open(OUT / "03_measured_mix_topics.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["topic", "mix_start_pct", "mix_end_pct", "mix_change", "female_start_pct", "female_end_pct",
                     "female_change", "start_values_used", "end_values_used", "within_contribution", "mix_contribution"])
    for t in SEVEN:
        writer.writerow([t, round(100 * main["w0"][t], 2), round(100 * main["w1"][t], 2),
                         round(100 * (main["w1"][t] - main["w0"][t]), 2),
                         round(100 * main["f0"][t], 2), round(100 * main["f1"][t], 2),
                         round(100 * (main["f1"][t] - main["f0"][t]), 2), main["n0"][t], main["n1"][t],
                         round(100 * main["by_topic_within"][t], 2), round(100 * main["by_topic_mix"][t], 2)])

print(f"{'spec':15} {'actual':>7} {'within':>7} {'mix':>7} {'unexpl':>7} {'within%':>8} {'mix%':>7} {'rebuilt start':>14} {'rebuilt end':>12}")
for r in runs:
    print(f"{r['name']:15} {100 * r['actual']:7.2f} {100 * r['within']:7.2f} {100 * r['mix']:7.2f} {100 * r['unexplained']:7.2f} "
          f"{100 * r['within'] / r['actual']:7.1f}% {100 * r['mix'] / r['actual']:6.1f}% {100 * r['rebuilt_start']:14.2f} {100 * r['rebuilt_end']:12.2f}")

print("\nMain result, by topic")
print(f"{'topic':21} {'mix start':>9} {'mix end':>8} {'female start':>12} {'(n)':>4} {'female end':>10} {'(n)':>4} {'within':>7} {'mix':>6}")
for t in SEVEN:
    print(f"{t:21} {100 * main['w0'][t]:9.1f} {100 * main['w1'][t]:8.1f} {100 * main['f0'][t]:12.1f} {main['n0'][t]:4} "
          f"{100 * main['f1'][t]:10.1f} {main['n1'][t]:4} {100 * main['by_topic_within'][t]:7.2f} {100 * main['by_topic_mix'][t]:6.2f}")


# ---------------------------------------------------------------------------
# Figure, written as SVG by hand because matplotlib is not installed.
# ---------------------------------------------------------------------------
WIDTH, LEFT, RIGHT, HEIGHT = 720, 44, 150, 690
PLOT_W = WIDTH - LEFT - RIGHT
INK = "fill:var(--ink2)"
other_three = [sum(mix_all[i][t] for t in THIN_START) for i in range(27)]
LINES = [
    ("Practical guidance", [m["Practical Guidance"] for m in mix_all], "--s2"),
    ("Seeking information", [m["Seeking information"] for m in mix_all], "--s3"),
    ("Other three topics", other_three, "--muted"),
    ("Writing", [m["Writing"] for m in mix_all], "--s1"),
    ("Technical help", [m["Technical help"] for m in mix_all], "--s4"),
]
A_TOP, A_H, A_LOW, A_HIGH = 120, 260, 0, 40
assert all(A_LOW / 100 <= v <= A_HIGH / 100 for _, series, _ in LINES for v in series), "top panel scale"


def x_at(i):
    return LEFT + PLOT_W * i / 26


def y_at(v):
    return A_TOP + A_H * (A_HIGH / 100 - v) / ((A_HIGH - A_LOW) / 100)


parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="t d" font-family="system-ui, -apple-system, 'Segoe UI', sans-serif">
<title id="t">Topic mix of ChatGPT messages in Norway, and the split of the rise in women's share</title>
<desc id="d">Top panel: each topic's share of all messages per month, July 2024 to September 2026. Writing falls and practical guidance rises. Bottom panel: the rise in women's share from the first to the last 3 months, split into a within-topic part, a mix part and an unexplained part. All values are in output/03_measured_mix.csv and output/03_measured_mix_topics.csv.</desc>
<style>
  svg {{ --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#6b6a66; --grid:rgba(11,11,11,.10); --axis:rgba(11,11,11,.45);
        --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#eda100; --s7:#6250d6; }}
  @media (prefers-color-scheme: dark) {{
    svg {{ --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7; --muted:#a3a29b; --grid:rgba(255,255,255,.10); --axis:rgba(255,255,255,.45);
          --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s7:#9085e9; }}
  }}
  text {{ fill:var(--ink2); font-size:13px; }}
  .title {{ fill:var(--ink); font-size:18px; font-weight:600; }}
  .head {{ fill:var(--ink); font-size:14px; font-weight:600; }}
  .small {{ fill:var(--muted); font-size:12px; }}
  .value {{ fill:var(--ink); font-size:13px; font-weight:600; }}
</style>
<rect width="{WIDTH}" height="{HEIGHT}" fill="var(--surface)"/>
<text x="16" y="30" class="title">Writing shrank, but the rise still came from within topics</text>
<text x="16" y="52">ChatGPT messages in Norway, July 2024 to September 2026</text>
<text x="16" y="86" class="head">Each topic's share of all messages</text>''']

# Legend, in the same order as the lines at their right end.
x = LEFT
for name, _, colour in LINES:
    parts.append(f'<line x1="{x}" x2="{x + 14}" y1="104" y2="104" stroke="var({colour})" stroke-width="2" stroke-linecap="round"/>')
    parts.append(f'<text x="{x + 18}" y="108" class="small">{name}</text>')
    x += 18 + 6.3 * len(name) + 14

for tick in range(A_LOW, A_HIGH + 1, 10):
    y = y_at(tick / 100)
    parts.append(f'<line x1="{LEFT}" x2="{LEFT + PLOT_W}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--grid)"/>')
    parts.append(f'<text x="{LEFT - 8}" y="{y + 4:.1f}" text-anchor="end" class="small">{tick}%</text>')
for i, m in enumerate(months):
    if m[5:7] in ("01", "07"):
        label = {"01": "Jan", "07": "Jul"}[m[5:7]] + " " + m[:4]
        anchor = "start" if i == 0 else "middle"
        parts.append(f'<text x="{x_at(i):.1f}" y="{A_TOP + A_H + 18}" text-anchor="{anchor}" class="small">{label}</text>')

for name, series, colour in LINES:
    points = " ".join(f"{x_at(i):.1f},{y_at(v):.1f}" for i, v in enumerate(series))
    parts.append(f'<polyline points="{points}" fill="none" stroke="var({colour})" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
    parts.append(f'<circle cx="{x_at(26):.1f}" cy="{y_at(series[26]):.1f}" r="4" fill="var({colour})" stroke="var(--surface)" stroke-width="2"/>')
    for i, v in enumerate(series):  # invisible hover targets, active when the file is opened directly
        parts.append(f'<circle cx="{x_at(i):.1f}" cy="{y_at(v):.1f}" r="7" fill="transparent"><title>{name}, {months[i]}: {100 * v:.1f} %</title></circle>')

# End labels. Lines that end close together get their labels moved apart by the minimum needed.
# This only works if LINES runs from the highest end value to the lowest.
end_values = [series[26] for _, series, _ in LINES]
assert end_values == sorted(end_values, reverse=True), "LINES must be ordered by end value"
label_y = []
for name, series, _ in LINES:
    y = y_at(series[26]) + 4
    if label_y and y - label_y[-1] < 15:
        y = label_y[-1] + 15
    label_y.append(y)
    parts.append(f'<text x="{x_at(26) + 10:.1f}" y="{y:.1f}" class="small" style="{INK}">{name.split()[0]} {100 * series[26]:.1f}%</text>')

# Bottom panel: the split of the main result, as bars from a zero line.
B_TOP, ROW = 468, 40
BARS = [("Actual rise in the total", main["actual"]), ("Within topics", main["within"]),
        ("Topic mix", main["mix"]), ("Not explained", main["unexplained"])]
B_LEFT, B_RIGHT = 190, WIDTH - 90
B_LOW, B_HIGH = -2, 12  # points
assert all(B_LOW <= 100 * v <= B_HIGH for _, v in BARS), "bottom panel scale"


def x_bar(points):
    return B_LEFT + (B_RIGHT - B_LEFT) * (points - B_LOW) / (B_HIGH - B_LOW)


parts.append('<text x="16" y="432" class="head">The rise from the first to the last 3 months, in percentage points</text>')
for tick in range(0, B_HIGH + 1, 4):
    parts.append(f'<line x1="{x_bar(tick):.1f}" x2="{x_bar(tick):.1f}" y1="{B_TOP - 8}" y2="{B_TOP + ROW * 4 - 8}" stroke="var({"--axis" if tick == 0 else "--grid"})"/>')
    parts.append(f'<text x="{x_bar(tick):.1f}" y="{B_TOP - 14}" text-anchor="middle" class="small">{tick}</text>')
for k, (name, value) in enumerate(BARS):
    points = 100 * value
    y0, h = B_TOP + k * ROW, 24
    x0, x1 = x_bar(0), x_bar(points)
    r = min(4, abs(x1 - x0))
    sign = 1 if points >= 0 else -1
    colour = "--ink2" if k == 0 else "--s7"
    parts.append(f'<path d="M{x0:.1f} {y0} H{x1 - sign * r:.1f} Q{x1:.1f} {y0} {x1:.1f} {y0 + r} V{y0 + h - r} Q{x1:.1f} {y0 + h} {x1 - sign * r:.1f} {y0 + h} H{x0:.1f} Z" fill="var({colour})"/>')
    parts.append(f'<text x="{B_LEFT - 34}" y="{y0 + 17}" text-anchor="end">{name}</text>')
    tip = max(x0, x1) + 8
    parts.append(f'<text x="{tip:.1f}" y="{y0 + 17}" class="value">{points:+.2f}</text>')

parts.append(f'<text x="16" y="{HEIGHT - 26}" class="small">Top: OpenAI\'s topic mix, rescaled to sum to 100 % each month. Other three: multimedia, self-expression, other/unknown.</text>')
parts.append(f'<text x="16" y="{HEIGHT - 8}" class="small">Bottom: all seven topics. Data: share_of_messages_by_topic_country_month.csv, norway_gender_topics_monthly.csv.</text>')
parts.append("</svg>")
(OUT / "03_measured_mix.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")

print("\nSaved output/03_measured_mix.csv, output/03_measured_mix_topics.csv and output/03_measured_mix.svg")
