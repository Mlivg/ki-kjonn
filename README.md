# ki-kjonn

A replication of the headline numbers on [kiindeksen.no/kjonn.html](https://kiindeksen.no/kjonn.html) ("Menn, kvinner og ChatGPT", 3 November 2026). The page finds no gender gap in work use of ChatGPT in Norway. Women send 50 % of work messages, and their jobs imply 50 %. This repository rebuilds those numbers from the page's own CSV files and reports what matches and what does not.

## Contents

| Section | What it covers |
|---|---|
| [Result](#result) | The page's numbers against ours |
| [Findings](#findings) | Small discrepancies and method choices |
| [Not checked](#not-checked) | What the published files cannot answer |
| [How to rerun](#how-to-rerun) | One command, no extra packages |
| [Files](#files) | Every file in the repository |
| [Data and licence](#data-and-licence) | Sources and terms |
| [How this was made](#how-this-was-made) | Claude Code, checked line by line |

## Result

All 13 numbers on the page round to the same whole percent in our calculation. At three decimals the expected share is 50.358 % and the observed share is 50.364 %.

| Number on the page | Page | Ours |
|---|---|---|
| Women's share of the employed (SSB, Q4 2025) | 47 | 47.35 |
| Expected share of work messages from women | 50 | 50.36 |
| Observed share of work messages from women | 50 | 50.36 |
| Expected, counted as persons, relationships, FTE | 50, 51, 49 | 50.36, 50.78, 49.38 |
| Writing, observed / expected | 57 / 55 | 56.69 / 54.71 |
| Technical help, observed / expected | 34 / 33 | 34.09 / 33.15 |
| Multimedia, observed / expected | 46 / 32 | 46.01 / 32.42 |
| Multimedia share of work messages | 4 | 4.03 |

The full table is in [output/01_replicate_headline.csv](output/01_replicate_headline.csv).

## Findings

1. **The 50/50 depends on the topic weights.** The topics file has two weight columns. The page's result comes from `topic_share_work_openai`, the topic shares OpenAI reports. With `share_of_work_messages`, the shares implied by the activity key, expected is 49.18 % and observed is 49.36 %. The gap stays small with both.
2. **The page uses both weights.** The 50 % uses OpenAI's topic shares. The statement that multimedia is 4 % of work messages uses the other column. With OpenAI's shares, multimedia is 5.9 %.
3. **The total matches partly because topic gaps offset each other.** Practical guidance has 51.95 % observed against 56.42 % expected. It is a quarter of work messages and pulls the total down by 1.12 points, more than any other topic. Multimedia (+0.79) and writing (+0.76) pull it up.

| Topic | Weight | Observed minus expected | Contribution to total |
|---|---|---|---|
| Practical guidance | 0.251 | −4.47 | −1.12 |
| Seeking information | 0.133 | −3.26 | −0.43 |
| Other/unknown | 0.055 | −2.97 | −0.16 |
| Self-expression | 0.025 | +3.38 | +0.09 |
| Technical help | 0.096 | +0.94 | +0.09 |
| Writing | 0.382 | +1.98 | +0.76 |
| Multimedia | 0.059 | +13.59 | +0.79 |

4. **The data dictionary gives an older observed value.** It states 49.4 %. That matches the other weighting (49.36 %), not the page's 50.
5. **The 47 % includes occupation code 0000.** That code means occupation unknown. Without it, women are 48.10 % of the employed.
6. **Observed per topic is a plain monthly mean.** It equals the unweighted mean of the published months from October 2025 to September 2026. Multimedia and technical help have 7 of 12 months.

Details and the reasoning behind each point are in [output/01_replicate_headline_notes.md](output/01_replicate_headline_notes.md).

## Not checked

1. **Expected per topic from scratch.** The activity file has no topic column. The key from activity to topic is not among the published files, so the expected value for each topic cannot be rebuilt here.
2. **An open gap.** Weighting each activity's women's share by its ChatGPT share gives 48.14 % expected, not 49.18 %. The topic key is needed to see why.
3. **The `ratio` column** in the activity file. Its exact definition is not confirmed.

## How to rerun

Python 3.9 or newer. No extra packages.

```bash
python3 -I scripts/01_replicate_headline.py
```

The script reads only `data/raw` and writes `output/01_replicate_headline.csv`. It prints the comparison table and the extra checks above.

## Files

| Path | Content |
|---|---|
| [scripts/01_replicate_headline.py](scripts/01_replicate_headline.py) | The replication pipeline |
| [output/01_replicate_headline.csv](output/01_replicate_headline.csv) | Page number, our number and status for each headline number |
| [output/01_replicate_headline_notes.md](output/01_replicate_headline_notes.md) | Method choices, discrepancies and open questions |
| `data/raw/` | The page's data files, unchanged (see below) |
| [session-log.md](session-log.md) | What was done in each work session |
| [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md) | Instructions for the coding agent |

Files in `data/raw`, downloaded from [kiindeksen.no/data/openai_signals/](https://kiindeksen.no/data/openai_signals/) on 2026-11-03:

| File | Content |
|---|---|
| `ssb_12542_sysselsatte_yrke4_kjonn.csv` | Employed persons per occupation (STYRK-08) and gender, Q4 2015 to 2025 |
| `activities_gender_norway.csv` | 332 O*NET work activities, 164 reported by OpenAI, with gender split of the work and ChatGPT share |
| `topics_expected_observed_persons.csv` | Seven topics times three ways of counting jobs, expected and observed share of women |
| `norway_gender_topics_monthly.csv` | Observed share of messages from female names per month and topic, July 2024 to September 2026 |
| `styrk08_openai_gender_persons.csv` | 390 occupations with ChatGPT use per worker by gender |
| `openai_signals_data_dictionary.md` | The page's data dictionary (Norwegian) |

## Data and licence

- OpenAI Signals v3.0, Chatterji et al. (2026), CC BY 4.0. [openai.com/signals/data-download](https://openai.com/signals/data-download/)
- Statistics Norway (SSB), table 12542.
- The link from O*NET activities to STYRK-08 and the files above are by Hernæs and Kostøl for [KI-indeksen](https://kiindeksen.no).

## How this was made

The pipeline was written with Claude Code. Every line was then reviewed by hand. The review changed one thing: Python's `round()` rounds 50.5 down to 50, so the script uses round-half-up instead. No result changed. The raw files were checked byte for byte against the live files on kiindeksen.no after the analysis.

## Folder context

- Storage: local folder, to be pushed to [github.com/Mlivg/ki-kjonn](https://github.com/Mlivg/ki-kjonn).
- Authoritative path: `/Users/marialivgard/AI Agent stuff/KI index kjønn`.
- Standalone project. Not part of the AABE course folder.
- Instructions for agents: `AGENTS.md`. Log and handovers: `session-log.md`.
