# ki-kjonn

Three analyses of the numbers on [kiindeksen.no/kjonn.html](https://kiindeksen.no/kjonn.html) ("Menn, kvinner og ChatGPT", 3 November 2026). The page finds no gender gap in work use of ChatGPT in Norway. Women send 50 % of work messages, and their jobs imply 50 %. Analysis 01 rebuilds those numbers from the page's own CSV files and reports what matches and what does not. Analysis 02 asks a question the page leaves open: did women's share rise within topics, or did the topic mix shift? Analysis 03 answers the same question with OpenAI's measured monthly topic mix.

Website: [mlivg.github.io/ki-kjonn](https://mlivg.github.io/ki-kjonn/)

## Contents

| Section | What it covers |
|---|---|
| [Analysis 01: replication](#analysis-01-replication) | The page's numbers against ours |
| [Result](#result) | All 13 numbers compared |
| [Findings](#findings) | Small discrepancies and method choices |
| [Not checked](#not-checked) | What the published files cannot answer |
| [Analysis 02: within topics or topic mix?](#analysis-02-within-topics-or-topic-mix) | What drove the rise in women's share over time |
| [Analysis 03: the measured topic mix](#analysis-03-the-measured-topic-mix) | The same split with OpenAI's monthly topic mix |
| [How to rerun](#how-to-rerun) | One command per analysis, no extra packages |
| [Files](#files) | Every file in the repository |
| [Data and licence](#data-and-licence) | Sources and terms |
| [How this was made](#how-this-was-made) | Claude Code and the checks that were run |

## Analysis 01: replication

### Result

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

### Findings

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

### Not checked

1. **Expected per topic from scratch.** The activity file has no topic column. The key from activity to topic is not among the published files, so the expected value for each topic cannot be rebuilt here.
2. **An open gap.** Weighting each activity's women's share by its ChatGPT share gives 48.14 % expected, not 49.18 %. The topic key is needed to see why.
3. **The `ratio` column** in the activity file. Its exact definition is not confirmed.

## Analysis 02: within topics or topic mix?

Women's share of ChatGPT messages rose from 35.1 % in July 2024 to 48.6 % in September 2026. Most of that rise happened within topics.

On the first and last 3 months, the total rose 10.43 points. With the topic mix held fixed, four topics give a rise of 10.51 points. That leaves −0.07 points for the mix.

| Topic | Weight | First 3 months | Last 3 months | Rise (points) |
|---|---|---|---|---|
| Technical help | 0.096 | 20.4 % | 34.5 % | 14.1 |
| Practical guidance | 0.251 | 38.4 % | 52.0 % | 13.6 |
| Seeking information | 0.133 | 32.1 % | 42.7 % | 10.6 |
| Writing | 0.382 | 49.8 % | 57.3 % | 7.5 |
| **All messages** | | **39.1 %** | **49.5 %** | **10.4** |

The monthly topic mix is not published, so the mix effect is what remains and is not measured directly. Any fixed weights on these four topics give a rise between 7.5 and 14.1 points. Across all tests, the mix can explain at most 3.63 points under such weights.

The result does not show why women's share rose. It could be more women using ChatGPT, or the same women sending more messages. Three topics with too few early values are left out of the main result.

Method, tests and limits are in [output/02_shift_share_notes.md](output/02_shift_share_notes.md). The figure is [output/02_shift_share.svg](output/02_shift_share.svg).

## Analysis 03: the measured topic mix

OpenAI's download has each topic's share of messages in Norway for all 27 months, so the mix can be measured. The within-topic rise explains nearly all of the increase. From the first 3 to the last 3 months:

| Part | Points |
|---|---|
| Within topics | +10.56 |
| Topic mix | −0.74 |
| Not explained | +0.61 |
| **Actual rise** | **+10.43** |

Writing fell from 34.7 % to 17.5 % of messages. That lowers the total by 1.65 points, because women's share is high in Writing. The fall in Technical help raises it by 1.20 points, because women's share is low there. Across the tests, the mix stays between −1.06 and +0.57 points.

The results are consistent with women catching up in their use of individual ChatGPT accounts in Norway. The data cannot show whether women are catching up in AI use overall, because business accounts, Codex and other AI tools are not included.

Analysis 02's conclusion holds. Its fixed weights differed a lot from the measured mix, so the close match between its 10.51 and this 10.56 is partly luck.

Three topics have little early data, so their start shares are uncertain. The note shows how the result moves if they change, and how the published total limits them. It also lists the other limits and what was not checked.

Details are in [output/03_measured_mix_notes.md](output/03_measured_mix_notes.md). The figure is [output/03_measured_mix.svg](output/03_measured_mix.svg).

## How to rerun

Python 3.9 or newer. No extra packages.

```bash
python3 -I scripts/01_replicate_headline.py
```

```bash
python3 -I scripts/02_shift_share.py
```

```bash
python3 -I scripts/03_measured_mix.py
```

Scripts 01 and 02 read only `data/raw`. Script 03 also reads `data/raw_openai_signals`. Each script writes its results to `output/` and prints its main table and extra checks. Scripts 02 and 03 run their tests on made-up data first, and stop if one fails.

## Files

| Path | Content |
|---|---|
| [scripts/01_replicate_headline.py](scripts/01_replicate_headline.py) | The replication pipeline |
| [output/01_replicate_headline.csv](output/01_replicate_headline.csv) | Page number, our number and status for each headline number |
| [output/01_replicate_headline_notes.md](output/01_replicate_headline_notes.md) | Method choices, discrepancies and open questions |
| [scripts/02_shift_share.py](scripts/02_shift_share.py) | The within-topic and topic-mix split, with its tests |
| [output/02_shift_share.csv](output/02_shift_share.csv) | The main result and seven tests of its choices |
| [output/02_shift_share.svg](output/02_shift_share.svg) | Figure of women's share by topic and in total |
| [output/02_shift_share_notes.md](output/02_shift_share_notes.md) | Result, method, limits and what was not checked |
| [scripts/03_measured_mix.py](scripts/03_measured_mix.py) | The split with the measured topic mix, with its tests |
| [output/03_measured_mix.csv](output/03_measured_mix.csv) | The main result and eleven tests of its choices |
| [output/03_measured_mix_topics.csv](output/03_measured_mix_topics.csv) | The main result, topic by topic |
| [output/03_measured_mix.svg](output/03_measured_mix.svg) | Figure of the topic mix over time and the split |
| [output/03_measured_mix_notes.md](output/03_measured_mix_notes.md) | Result, method, tests, limits and what was not checked |
| [index.html](index.html) | The website, listing the analyses |
| `data/raw/` | The page's data files, unchanged (see below) |
| `data/raw_openai_signals/` | OpenAI's Signals download, unchanged (see below) |
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

`data/raw_openai_signals/` holds the 25 files in [OpenAI's download](https://cdn.openai.com/signals/data-download-csv.zip), downloaded on 2026-11-09: 24 CSV files, and `README.pdf`, which is OpenAI's data dictionary. Analysis 03 uses four of the CSV files.

## Data and licence

- OpenAI Signals v3.0, Chatterji et al. (2026), CC BY 4.0. [openai.com/signals/data-download](https://openai.com/signals/data-download/)
- Statistics Norway (SSB), table 12542.
- The link from O*NET activities to STYRK-08 and the files above are by Hernæs and Kostøl for [KI-indeksen](https://kiindeksen.no).

## How this was made

The scripts were written with Claude Code.

In analysis 01, the review changed one thing: Python's `round()` rounds 50.5 down to 50, so the script uses round-half-up instead. No result changed. The raw files were checked byte for byte against the live files on kiindeksen.no after the analysis.

In analysis 02, the tests on made-up data stopped eight of nine bugs planted on purpose. The ninth ignored the weights, so a new test now stops it too. A separate short script gave the same main result. A clean copy with only the script and `data/raw` gave byte-identical output.

In analysis 03, the tests on made-up data stopped all ten bugs planted on purpose. A separate short script gave the same main result. A clean copy with only the script and the two data folders gave byte-identical output.

## Folder context

- Storage: a local Git repository, pushed to [github.com/Mlivg/ki-kjonn](https://github.com/Mlivg/ki-kjonn).
- Not in this repository: `data/raw/kjonn.html`, a saved copy of the page. Use the live page instead.
- Standalone project. Not part of the AABE course folder.
- Instructions for agents: `AGENTS.md`. Log and handovers: `session-log.md`.
