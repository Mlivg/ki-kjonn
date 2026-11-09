"""Split the rise in women's share of ChatGPT messages in Norway.

Question: did the share rise because women's share grew within topics, or
because the mix of topics shifted?

The monthly file gives women's share per topic and in total, but not each
topic's share of messages per month. So the mix effect cannot be measured
directly. This script:
  1. measures the rise within each topic,
  2. combines those rises with one fixed set of topic weights,
  3. treats the rest of the actual rise as the part left over for the mix,
  4. reports the range that any fixed weights on the four topics could give.

Reads only data/raw. Writes output/02_shift_share.csv and output/02_shift_share.svg.
Uses the Python standard library only. The tests on made-up data run first.
If one fails, the script stops before it reads the real data.

Run from the project folder:
    python3 -I scripts/02_shift_share.py
"""

import csv
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "output"

# These four topics have a value in each of the first three months. The other three do not.
FOUR = ["Writing", "Practical Guidance", "Seeking information", "Technical help"]
OTHER_THREE = ["Multimedia", "Self-expression", "Other/Unknown"]
W_OPENAI = "topic_share_work_openai"
W_KEY = "share_of_work_messages"


# ---------------------------------------------------------------------------
# The method. Every function takes shares between 0 and 1.
# ---------------------------------------------------------------------------
def fill_gaps(series, nearest_at_ends=False):
    """Return a copy with gaps filled by a straight line between neighbours.

    A gap before the first value or after the last value has only one
    neighbour. It stays empty unless nearest_at_ends is True.
    """
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


def window_mean(series, positions):
    """Mean of the values at these positions, skipping gaps. Also returns the count."""
    values = [series[i] for i in positions if series[i] is not None]
    return (sum(values) / len(values) if values else None), len(values)


def decompose(topics, total, weights, start, end):
    """Compare two windows of months.

    topics:  {topic name: list of monthly shares}
    total:   list of monthly shares for all messages
    weights: {topic name: fixed weight}
    start, end: lists of month positions

    fixed_mix_rise is the rise in the total if the topic weights never change.
    left_for_mix is the actual rise minus that.
    """
    rises, counts = {}, {}
    for name, series in topics.items():
        a, n_a = window_mean(series, start)
        b, n_b = window_mean(series, end)
        counts[name] = (n_a, n_b)
        if a is not None and b is not None:
            rises[name] = b - a
    total_weight = sum(weights[name] for name in rises)
    fixed_mix_rise = sum(weights[name] * rises[name] for name in rises) / total_weight
    total_start = window_mean(total, start)[0]
    total_end = window_mean(total, end)[0]
    actual = total_end - total_start
    return {
        "rises": rises,
        "counts": counts,
        "total_start": total_start,
        "total_end": total_end,
        "actual": actual,
        "fixed_mix_rise": fixed_mix_rise,
        "left_for_mix": actual - fixed_mix_rise,
        "lowest": min(rises.values()),
        "highest": max(rises.values()),
    }


# ---------------------------------------------------------------------------
# Tests on made-up data, where the right answer is known.
# ---------------------------------------------------------------------------
def close(a, b):
    return abs(a - b) < 1e-9


def made_up(weights_start, weights_end, shares_start, shares_end):
    """Two months of data. The total follows the true weights of each month."""
    topics = {t: [shares_start[t], shares_end[t]] for t in shares_start}
    total = [sum(weights_start[t] * shares_start[t] for t in topics),
             sum(weights_end[t] * shares_end[t] for t in topics)]
    return topics, total


def run_tests():
    # Both effects at once. By hand: within 10 points, mix 9 points, total 19 points.
    w0 = {"A": 0.2, "B": 0.3, "C": 0.5}
    w1 = {"A": 0.5, "B": 0.3, "C": 0.2}
    f0 = {"A": 0.5, "B": 0.3, "C": 0.2}
    f1 = {"A": 0.6, "B": 0.4, "C": 0.3}
    topics, total = made_up(w0, w1, f0, f1)
    r = decompose(topics, total, w1, [0], [1])
    assert close(r["actual"], 0.19), "total rise"
    assert close(r["fixed_mix_rise"], 0.10), "within part"
    assert close(r["left_for_mix"], 0.09), "mix part"

    # Only the mix moves. The within part must be zero.
    topics, total = made_up(w0, w1, f0, f0)
    r = decompose(topics, total, w1, [0], [1])
    assert close(r["fixed_mix_rise"], 0.0), "pure mix: within part"
    assert close(r["left_for_mix"], r["actual"]), "pure mix: all left over"

    # Only the shares within topics move. Nothing is left for the mix.
    topics, total = made_up(w1, w1, f0, f1)
    r = decompose(topics, total, w1, [0], [1])
    assert close(r["left_for_mix"], 0.0), "pure within: nothing left over"

    # Any weights must give a result between the lowest and highest topic rise.
    topics = {"A": [0.1, 0.2], "B": [0.1, 0.5]}
    for wa in (0.0, 0.25, 0.5, 1.0):
        r = decompose(topics, [0.1, 0.3], {"A": wa, "B": 1 - wa}, [0], [1])
        assert r["lowest"] - 1e-9 <= r["fixed_mix_rise"] <= r["highest"] + 1e-9, "range"
        # The rises differ here (10 and 40 points), so this checks that the weights are used.
        assert close(r["fixed_mix_rise"], wa * 0.1 + (1 - wa) * 0.4), "weighted mean"

    # Gaps: skipped in a window, filled on a straight line, ends only on request.
    assert close(window_mean([0.2, None, 0.4], [0, 1, 2])[0], 0.3), "gap skipped in mean"
    assert window_mean([0.2, None, 0.4], [0, 1, 2])[1] == 2, "gap skipped in count"
    assert close(fill_gaps([0.1, None, None, 0.4])[1], 0.2), "straight line"
    assert fill_gaps([None, 0.1])[0] is None, "start stays empty"
    assert fill_gaps([None, 0.1], nearest_at_ends=True)[0] == 0.1, "nearest value"

    # A topic with no value in a window drops out and the weights rescale.
    topics = {"A": [0.1, 0.2], "B": [None, 0.9]}
    r = decompose(topics, [0.1, 0.2], {"A": 0.5, "B": 0.5}, [0], [1])
    assert "B" not in r["rises"] and close(r["fixed_mix_rise"], 0.1), "topic dropped"


run_tests()
print("Tests on made-up data passed.\n")


# ---------------------------------------------------------------------------
# Real data.
# ---------------------------------------------------------------------------
def read(name):
    with open(RAW / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


monthly = read("norway_gender_topics_monthly.csv")
assert len(monthly) == 27, "expected 27 months"
months = [m["month"][:7] for m in monthly]
panel = {t: [float(m[t]) if m[t] else None for m in monthly] for t in FOUR + OTHER_THREE}
alle = [float(m["Alle"]) for m in monthly]

persons = [t for t in read("topics_expected_observed_persons.csv") if t["baseline"] == "persons"]
openai = {t["topic"]: float(t[W_OPENAI]) for t in persons}
key = {t["topic"]: float(t[W_KEY]) for t in persons}
assert set(openai) == set(FOUR + OTHER_THREE), "topic names must match across files"

first = lambda n: list(range(n))
last = lambda n: list(range(len(months) - n, len(months)))
four = {t: panel[t] for t in FOUR}
four_filled = {t: fill_gaps(panel[t]) for t in FOUR}
seven_filled = {t: fill_gaps(panel[t], nearest_at_ends=True) for t in panel}
complete = [i for i in range(len(months)) if all(panel[t][i] is not None for t in FOUR)]

# The first row is the main result, chosen before the other rows were run.
# The other rows test its choices.
SPECS = [
    ("main", "Four topics, OpenAI weights, first and last 3 months, gaps skipped",
     four, openai, first(3), last(3)),
    ("other_weights", "Same, with the weights implied by the activity key",
     four, key, first(3), last(3)),
    ("gaps_filled", "Same as main, gaps filled on a straight line first",
     four_filled, openai, first(3), last(3)),
    ("complete_months", "First and last 3 months with all four topics published",
     four, openai, complete[:3], complete[-3:]),
    ("six_months", "First and last 6 months, gaps skipped",
     four, openai, first(6), last(6)),
    ("twelve_months", "First and last 12 months, gaps skipped",
     four, openai, first(12), last(12)),
    ("single_months", "July 2024 against September 2026, as on the page",
     four, openai, first(1), last(1)),
    ("seven_topics", "All seven topics, gaps filled, nearest value at the ends",
     seven_filled, openai, first(3), last(3)),
]

rows = []
results = {}
for name, description, topics, weights, start, end in SPECS:
    r = decompose(topics, alle, weights, start, end)
    results[name] = r
    has_range = name != "seven_topics"  # filled start values make this topic range misleading
    rows.append({
        "spec": name,
        "description": description,
        "start_months": " ".join(months[i] for i in start),
        "end_months": " ".join(months[i] for i in end),
        "alle_start_pct": round(100 * r["total_start"], 2),
        "alle_end_pct": round(100 * r["total_end"], 2),
        "actual_rise": round(100 * r["actual"], 2),
        "fixed_mix_rise": round(100 * r["fixed_mix_rise"], 2),
        "left_for_mix": round(100 * r["left_for_mix"], 2),
        "fixed_mix_share_of_rise_pct": round(100 * r["fixed_mix_rise"] / r["actual"], 1),
        "lowest_topic_rise": round(100 * r["lowest"], 2) if has_range else "",
        "highest_topic_rise": round(100 * r["highest"], 2) if has_range else "",
        "most_left_for_mix": round(100 * (r["actual"] - r["lowest"]), 2) if has_range else "",
        "rise_writing": round(100 * r["rises"]["Writing"], 2),
        "rise_practical_guidance": round(100 * r["rises"]["Practical Guidance"], 2),
        "rise_seeking_information": round(100 * r["rises"]["Seeking information"], 2),
        "rise_technical_help": round(100 * r["rises"]["Technical help"], 2),
        "values_used_technical_help": "{}+{}".format(*r["counts"]["Technical help"]),
        "values_used_writing": "{}+{}".format(*r["counts"]["Writing"]),
    })

# What if the three left-out topics did not rise at all? Their weights stay in the
# denominator and add nothing to the top.
main = results["main"]
sum_all = sum(openai.values())
zero_floor = sum(openai[t] * main["rises"][t] for t in FOUR) / sum_all
four_weight = sum(openai[t] for t in FOUR) / sum_all

# Level check: the fixed-mix line should sit close to the published total.
fixed_line = [sum(openai[t] * four_filled[t][i] for t in FOUR) / sum(openai[t] for t in FOUR)
              for i in range(len(months))]
level_diff = [fixed_line[i] - alle[i] for i in range(len(months))]

OUT.mkdir(exist_ok=True)
with open(OUT / "02_shift_share.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

print(f"{'spec':17} {'actual':>7} {'fixed mix':>10} {'left':>7} {'share':>7} {'low':>6} {'high':>6}")
for r in rows:
    print(f"{r['spec']:17} {r['actual_rise']:>7.2f} {r['fixed_mix_rise']:>10.2f} {r['left_for_mix']:>7.2f} "
          f"{r['fixed_mix_share_of_rise_pct']:>6.1f}% {str(r['lowest_topic_rise']):>6} {str(r['highest_topic_rise']):>6}")

print("\nMain result, by topic")
for t in FOUR:
    a, n_a = window_mean(panel[t], first(3))
    b, n_b = window_mean(panel[t], last(3))
    print(f"  {t:20} weight={openai[t]:.3f}  start={100 * a:5.1f} ({n_a})  end={100 * b:5.1f} ({n_b})  rise={100 * (b - a):5.1f}")

print("\nOther checks")
print(f"  months with all four topics published: {len(complete)} of {len(months)}")
print(f"  share of the OpenAI weights in the four topics: {100 * four_weight:.1f} %")
print(f"  fixed-mix rise if the other three topics did not rise: {100 * zero_floor:.2f} points")
print(f"  fixed-mix line minus Alle, by month: lowest {100 * min(level_diff):+.2f}, highest {100 * max(level_diff):+.2f} points")
print(f"  same in the first 3 months: {100 * sum(level_diff[:3]) / 3:+.2f}, in the last 3 months: {100 * sum(level_diff[-3:]) / 3:+.2f} points")


# ---------------------------------------------------------------------------
# Figure, written as SVG by hand because matplotlib is not installed.
# ---------------------------------------------------------------------------
WIDTH, LEFT, RIGHT = 720, 44, 140
PLOT_W = WIDTH - LEFT - RIGHT
SERIES = {
    "Writing": "--s1",
    "Practical Guidance": "--s2",
    "Seeking information": "--s3",
    "Technical help": "--s4",
}
LABEL = {"Practical Guidance": "Practical guidance", "Seeking information": "Seeking information",
         "Writing": "Writing", "Technical help": "Technical help"}


def x_at(i):
    return LEFT + PLOT_W * i / (len(months) - 1)


def month_label(m):
    return {"01": "Jan", "07": "Jul"}[m[5:7]] + " " + m[:4]


def line(series, colour, name, y_at):
    """One line. A gap in the data breaks the line. A lone value becomes a dot."""
    parts, run = [], []
    for i, v in enumerate(series + [None]):
        if v is not None:
            run.append(i)
            continue
        if len(run) > 1:
            pts = " ".join(f"{x_at(k):.1f},{y_at(series[k]):.1f}" for k in run)
            parts.append(f'<polyline points="{pts}" fill="none" stroke="var({colour})" stroke-width="2" '
                         'stroke-linejoin="round" stroke-linecap="round"/>')
        elif run:
            k = run[0]
            parts.append(f'<circle cx="{x_at(k):.1f}" cy="{y_at(series[k]):.1f}" r="4" fill="var({colour})" '
                         'stroke="var(--surface)" stroke-width="2"/>')
        run = []
    end = max(i for i, v in enumerate(series) if v is not None)
    parts.append(f'<circle cx="{x_at(end):.1f}" cy="{y_at(series[end]):.1f}" r="4" fill="var({colour})" '
                 'stroke="var(--surface)" stroke-width="2"/>')
    for i, v in enumerate(series):  # invisible hover targets, active when the file is opened directly
        if v is not None:
            parts.append(f'<circle cx="{x_at(i):.1f}" cy="{y_at(v):.1f}" r="8" fill="transparent">'
                         f'<title>{escape(name)}, {months[i]}: {100 * v:.1f} %</title></circle>')
    return "\n".join(parts)


def panel_frame(top, height, low, high, step, y_at):
    parts = []
    w = PLOT_W / (len(months) - 1)
    for a, b, text in ((0, 2, "First 3"), (len(months) - 3, len(months) - 1, "Last 3")):
        x0 = max(LEFT, x_at(a) - w / 2)
        x1 = min(LEFT + PLOT_W, x_at(b) + w / 2)
        parts.append(f'<rect x="{x0:.1f}" y="{top}" width="{x1 - x0:.1f}" height="{height}" fill="var(--band)"/>')
        parts.append(f'<text x="{(x0 + x1) / 2:.1f}" y="{top + 14}" text-anchor="middle" class="small">{text}</text>')
    tick = low
    while tick <= high:
        y = y_at(tick / 100)
        parts.append(f'<line x1="{LEFT}" x2="{LEFT + PLOT_W}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--grid)"/>')
        parts.append(f'<text x="{LEFT - 8}" y="{y + 4:.1f}" text-anchor="end" class="small">{tick}%</text>')
        tick += step
    for i, m in enumerate(months):
        if m[5:7] in ("01", "07"):
            anchor = "start" if i == 0 else "middle"
            parts.append(f'<text x="{x_at(i):.1f}" y="{top + height + 18}" text-anchor="{anchor}" class="small">{month_label(m)}</text>')
    return "\n".join(parts)


def legend(y, items):
    parts, x = [], LEFT
    for colour, text in items:
        parts.append(f'<line x1="{x}" x2="{x + 16}" y1="{y - 4}" y2="{y - 4}" stroke="var({colour})" stroke-width="2" stroke-linecap="round"/>')
        parts.append(f'<text x="{x + 21}" y="{y}" class="small">{escape(text)}</text>')
        x += 21 + 6.6 * len(text) + 18
    return "\n".join(parts)


def end_label(series, y_at, text):
    end = max(i for i, v in enumerate(series) if v is not None)
    return (f'<text x="{x_at(end) + 10:.1f}" y="{y_at(series[end]) + 4:.1f}" class="small ink">'
            f'{escape(text)} {100 * series[end]:.1f}%</text>')


A_TOP, A_H, A_LOW, A_HIGH = 118, 250, 10, 70
B_TOP, B_H, B_LOW, B_HIGH = 462, 190, 30, 60
y_a = lambda v: A_TOP + A_H * (A_HIGH / 100 - v) / ((A_HIGH - A_LOW) / 100)
y_b = lambda v: B_TOP + B_H * (B_HIGH / 100 - v) / ((B_HIGH - B_LOW) / 100)

# The scales are set by hand. Stop if new data would be drawn outside a panel.
assert all(A_LOW / 100 <= v <= A_HIGH / 100 for t in FOUR for v in panel[t] if v is not None), "top panel scale"
assert all(B_LOW / 100 <= v <= B_HIGH / 100 for v in alle + fixed_line), "bottom panel scale"

svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} 730" role="img" aria-labelledby="t d" font-family="system-ui, -apple-system, 'Segoe UI', sans-serif">
<title id="t">Women's share of ChatGPT messages in Norway, by topic and in total</title>
<desc id="d">Top panel: monthly share of messages from women in four topics, July 2024 to September 2026. All four rise. Bottom panel: the published total against a line that holds the topic mix fixed. The two lines rise by a similar amount. All values are in output/02_shift_share.csv and data/raw/norway_gender_topics_monthly.csv.</desc>
<style>
  svg {{ --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#6b6a66; --grid:rgba(11,11,11,.10); --band:rgba(11,11,11,.05);
        --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#eda100; --s7:#6250d6; }}
  @media (prefers-color-scheme: dark) {{
    svg {{ --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7; --muted:#a3a29b; --grid:rgba(255,255,255,.10); --band:rgba(255,255,255,.06);
          --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s7:#9085e9; }}
  }}
  text {{ fill:var(--ink2); font-size:13px; }}
  .title {{ fill:var(--ink); font-size:18px; font-weight:600; }}
  .head {{ fill:var(--ink); font-size:14px; font-weight:600; }}
  .small {{ fill:var(--muted); font-size:12px; }}
  .ink {{ fill:var(--ink2); }}
</style>
<rect width="{WIDTH}" height="730" fill="var(--surface)"/>
<text x="{LEFT - 28}" y="30" class="title">Women's share of messages rose in every topic we can follow</text>
<text x="{LEFT - 28}" y="52">ChatGPT messages in Norway from typically female first names, July 2024 to September 2026</text>
<text x="{LEFT - 28}" y="86" class="head">Share of messages from women, by topic</text>''',
       legend(106, [(SERIES[t], LABEL[t]) for t in FOUR]),
       panel_frame(A_TOP, A_H, A_LOW, A_HIGH, 10, y_a)]
for t in FOUR:
    svg.append(line(panel[t], SERIES[t], LABEL[t], y_a))
    svg.append(end_label(panel[t], y_a, LABEL[t].split()[0]))
svg += [f'<text x="{LEFT - 28}" y="430" class="head">Published total against a fixed topic mix</text>',
        legend(450, [("--ink", "All messages (published)"), ("--s7", "Four topics, fixed mix")]),
        panel_frame(B_TOP, B_H, B_LOW, B_HIGH, 10, y_b),
        line(alle, "--ink", "All messages", y_b),
        line(fixed_line, "--s7", "Four topics, fixed mix", y_b),
        end_label(alle, y_b, "All"),
        end_label(fixed_line, y_b, "Fixed"),
        f'<text x="{LEFT - 28}" y="688" class="small">Top: breaks are months OpenAI withheld. Bottom: gaps filled on a straight line, weights from topic_share_work_openai.</text>',
        f'<text x="{LEFT - 28}" y="706" class="small">Panels use different vertical scales. Data: norway_gender_topics_monthly.csv, topics_expected_observed_persons.csv.</text>',
        "</svg>"]
(OUT / "02_shift_share.svg").write_text("\n".join(svg) + "\n", encoding="utf-8")

print("\nSaved output/02_shift_share.csv and output/02_shift_share.svg")
