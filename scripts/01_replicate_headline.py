"""Replicate the headline numbers on https://kiindeksen.no/kjonn.html.

Reads only data/raw. Writes output/01_replicate_headline.csv.
Uses the Python standard library only (pandas is not installed).

Run from the project folder:
    python3 -I scripts/01_replicate_headline.py
"""

import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "output"

# Numbers as printed on the page (data/raw/kjonn.html, downloaded 2026-11-03).
# All are whole percent, so a match means "rounds to the same whole percent".
PAGE = {
    "women_share_employed": 47,
    "expected_all": 50,
    "observed_all": 50,
    "expected_writing": 55,
    "observed_writing": 57,
    "expected_technical": 33,
    "observed_technical": 34,
    "expected_multimedia": 32,
    "observed_multimedia": 46,
    "multimedia_share_of_work_messages": 4,
    "expected_persons": 50,  # "Tre måter å telle jobber på gir 49, 50 og 51"
    "expected_relationships": 51,
    "expected_fte": 49,
}


def read(name):
    """Return a CSV file in data/raw as a list of dicts (one per row)."""
    with open(RAW / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def weighted_mean(rows, value, weight):
    """Sum of weight * value divided by the sum of weights."""
    total_w = sum(float(r[weight]) for r in rows)
    return sum(float(r[weight]) * float(r[value]) for r in rows) / total_w


results = []  # rows for the output table


def report(key, ours, note):
    """Store one comparison. `ours` is a share between 0 and 1."""
    pct = 100 * ours
    page = PAGE[key]
    # Round half up. Python's round() rounds 50.5 to 50 (to even), which is not
    # how a published percent is rounded.
    match = "match" if math.floor(pct + 0.5) == page else "NOT MATCHED"
    results.append({"number": key, "page_pct": page, "ours_pct": round(pct, 2),
                    "status": match, "how": note})


# ---------------------------------------------------------------------------
# 1. Women's share of the employed: SSB table 12542, 4th quarter 2025.
# ---------------------------------------------------------------------------
ssb = [r for r in read("ssb_12542_sysselsatte_yrke4_kjonn.csv") if r["year"] == "2025"]
women = sum(int(r["employed"]) for r in ssb if r["kjonn"] == "kvinner")
men = sum(int(r["employed"]) for r in ssb if r["kjonn"] == "menn")
report("women_share_employed", women / (women + men),
       f"SSB 12542, 2025, all codes incl. 0000 (unknown): {women} women, {men} men")

# Same without code 0000 (occupation unknown), to show the choice matters.
w_known = sum(int(r["employed"]) for r in ssb if r["kjonn"] == "kvinner" and r["styrk08"] != "0000")
m_known = sum(int(r["employed"]) for r in ssb if r["kjonn"] == "menn" and r["styrk08"] != "0000")
women_share_known = w_known / (w_known + m_known)

# ---------------------------------------------------------------------------
# 2. Expected and observed, all work messages.
#    The topic file has two candidate weights per topic:
#      share_of_work_messages   = topic share implied by the activity key
#      topic_share_work_openai  = topic share of work messages as OpenAI reports it
#    The page says topics are weighted "slik arbeidsmeldingene fordeler seg".
# ---------------------------------------------------------------------------
topics = read("topics_expected_observed_persons.csv")
by_base = {b: [t for t in topics if t["baseline"] == b] for b in ("persons", "relationships", "fte")}
persons = by_base["persons"]

W_OPENAI = "topic_share_work_openai"
W_KEY = "share_of_work_messages"

report("expected_all", weighted_mean(persons, "expected", W_OPENAI), f"topics weighted by {W_OPENAI}")
report("observed_all", weighted_mean(persons, "observed", W_OPENAI), f"topics weighted by {W_OPENAI}")

alt_expected = weighted_mean(persons, "expected", W_KEY)
alt_observed = weighted_mean(persons, "observed", W_KEY)

# Three ways of counting jobs (page: 49, 50 and 51 expected).
for base in ("persons", "relationships", "fte"):
    report(f"expected_{base}", weighted_mean(by_base[base], "expected", W_OPENAI),
           f"baseline {base}, weighted by {W_OPENAI}")

# ---------------------------------------------------------------------------
# 3. Topic by topic (persons baseline).
# ---------------------------------------------------------------------------
topic = {t["topic"]: t for t in persons}
for key, name in (("writing", "Writing"), ("technical", "Technical help"), ("multimedia", "Multimedia")):
    report(f"expected_{key}", float(topic[name]["expected"]), f"{name}, expected column")
    report(f"observed_{key}", float(topic[name]["observed"]), f"{name}, observed column")

report("multimedia_share_of_work_messages", float(topic["Multimedia"][W_KEY]),
       f"Multimedia, {W_KEY} (with {W_OPENAI} it is {100 * float(topic['Multimedia'][W_OPENAI]):.1f} %)")

# ---------------------------------------------------------------------------
# 4. Observed per topic from the monthly series, October 2025 to September 2026.
#    Empty cells are months where no value is published. They are skipped.
# ---------------------------------------------------------------------------
monthly = [m for m in read("norway_gender_topics_monthly.csv") if "2025-10-01" <= m["month"] <= "2026-09-01"]
assert len(monthly) == 12, "expected 12 months in the window"
monthly_check = []
for name in topic:
    values = [float(m[name]) for m in monthly if m[name]]
    mean = sum(values) / len(values)
    diff = abs(mean - float(topic[name]["observed"]))
    monthly_check.append((name, len(values), mean, float(topic[name]["observed"]), diff))

# ---------------------------------------------------------------------------
# 5. Expected computed from the activity file, without the topic step.
#    For each activity: women's work in it / all work in it, using SSB 2025 persons.
#    Then weight activities by their share of Norway's work messages.
# ---------------------------------------------------------------------------
acts = [a for a in read("activities_gender_norway.csv") if a["reported"] == "1"]
assert len(acts) == 164


def women_share_of_activity(a):
    ww = women * float(a["work_share_women"])
    mw = men * float(a["work_share_men"])
    return ww / (ww + mw)


expected_activity_level = sum(float(a["chatgpt_share"]) * women_share_of_activity(a) for a in acts) / sum(
    float(a["chatgpt_share"]) for a in acts)

# ---------------------------------------------------------------------------
# Print and save.
# ---------------------------------------------------------------------------
OUT.mkdir(exist_ok=True)
out_file = OUT / "01_replicate_headline.csv"
with open(out_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(results[0]))
    writer.writeheader()
    writer.writerows(results)

print(f"{'number':36} {'page':>5} {'ours':>7}  status")
for r in results:
    print(f"{r['number']:36} {r['page_pct']:>5} {r['ours_pct']:>7.2f}  {r['status']}")

print("\nOther checks")
print(f"  women share without code 0000:            {100 * women_share_known:.2f} %")
print(f"  expected, weighted by {W_KEY}: {100 * alt_expected:.2f} %")
print(f"  observed, weighted by {W_KEY}: {100 * alt_observed:.2f} %")
print(f"  expected from activities, no topic step:  {100 * expected_activity_level:.2f} %")
print(f"  sum of {W_OPENAI}: {sum(float(t[W_OPENAI]) for t in persons):.5f}")
exp_all = weighted_mean(persons, "expected", W_OPENAI)
obs_all = weighted_mean(persons, "observed", W_OPENAI)
print(f"  expected vs observed, 3 decimals: {100 * exp_all:.3f} vs {100 * obs_all:.3f} %")
print(f"  each topic's contribution to observed minus expected ({W_OPENAI} weights, normalised):")
total_w = sum(float(t[W_OPENAI]) for t in persons)
for t in sorted(persons, key=lambda t: float(t[W_OPENAI]) * (float(t["observed"]) - float(t["expected"]))):
    gap = float(t["observed"]) - float(t["expected"])
    contrib = float(t[W_OPENAI]) / total_w * gap
    print(f"    {t['topic']:20} weight={float(t[W_OPENAI]):.3f}  gap={100 * gap:+6.2f} pp  contribution={100 * contrib:+.2f} pp")
print("  observed per topic vs mean of monthly values, Oct 2025 to Sep 2026:")
for name, n, mean, obs, diff in monthly_check:
    print(f"    {name:20} months={n:2}  monthly mean={mean:.5f}  file={obs:.5f}  diff={diff:.5f}")
print(f"\nSaved {out_file.relative_to(ROOT)}")
