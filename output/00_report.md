# Gender and ChatGPT use in Norway: six analyses of KI-indeksen's open data

10 November 2026. Each analysis has its own note, script and results in this repository.

## Key term

**Expected from jobs** is the share of work messages that would come from women if women and men in each occupation used ChatGPT equally for the tasks in that occupation. It combines SSB's counts of employed women and men in each occupation, O*NET's lists of tasks in each occupation, and OpenAI's figures for which tasks ChatGPT is used for in Norway.

## Summary

- The page's headline holds. Women send about half of work messages, the same as expected from jobs.
- Women's share of all messages rose from 39 % to about 50 % between mid-2024 and autumn 2026.
- Almost all of the rise happened within topics, not through a change in what ChatGPT is used for. The gaps between topics also narrowed.
- The rise slowed sharply in 2026, at about the level expected from jobs.
- Changes in where women work are far too slow to explain the rise.

## Data

The analyses use two folders of data. All files are kept exactly as downloaded.

**The page's files** (`data/raw`), downloaded from kiindeksen.no on 3 November 2026:

| File | Contents | Used in |
|---|---|---|
| `norway_gender_topics_monthly.csv` | Women's share of messages each month, July 2024 to September 2026, for seven topics and in total. 40 of 189 topic values are withheld. | 01 to 05 |
| `topics_expected_observed_persons.csv` | Expected and observed women's share for each topic, with two sets of topic weights. | 01, 02 |
| `activities_gender_norway.csv` | 332 work activities, 164 reported for Norway, with the gender split of the work and the share of ChatGPT use. | 01 |
| `ssb_12542_sysselsatte_yrke4_kjonn.csv` | Employed women and men in 407 occupations, 2015 to 2025. | 01, 06 |
| `styrk08_openai_gender_persons.csv` | ChatGPT use per worker in 390 occupations, calculated from tasks. | 06 |
| `openai_signals_data_dictionary.md` | Description of the files, in Norwegian. | |

**OpenAI's own files** (`data/raw_openai_signals`), downloaded from OpenAI Signals v3.0 on 9 November 2026. The download has 24 CSV files and OpenAI's data dictionary. They give shares of messages by country and month, broken down by topic, typical name gender, age group and work status. Analysis 03 uses four of them: the topic mix for all messages, the topic mix for work messages, women's share by topic and women's share overall. The last two are identical to the page's monthly file.

**Common features.** OpenAI samples 1 million messages a month worldwide from individual ChatGPT accounts. Business accounts and Codex are not included. Gender comes from first names, and a name counts only if more than 95 % of people with it share one gender. The files give shares, not message counts or user counts. OpenAI adds random noise to protect privacy, rounds shares to three decimals, and publishes a value only if it rests on at least 100 messages.

## Main findings

| | Question | Main finding |
|---|---|---|
| [01](01_replicate_headline_notes.md) | Do the page's numbers hold? | All 13 reproduce. Expected from jobs 50.36 %, observed 50.36 %. The result depends on the topic weights. |
| [02](02_shift_share_notes.md) | Within topics or topic mix? | With the mix held fixed, the rise is 10.51 points against an actual 10.43. The mix could explain at most 2.93. |
| [03](03_measured_mix_notes.md) | The same, with the measured mix | +10.56 points within topics, −0.74 from the mix, +0.61 not explained. |
| [04](04_topic_gaps_notes.md) | Are the topic gaps closing? | The gap between Writing and Technical help fell from 29.4 to 22.8 points. |
| [05](05_levelling_off_notes.md) | Has the rise levelled off? | +8.3 points in the first year, +2.1 in the second. The slowdown started in spring 2026. |
| [06](06_jobs_2015_2025_notes.md) | Did women move into high-use jobs? | Yes, faster than men from 2015 to 2025: +2.7 points against +1.3. |

## Connections

**1. Women caught up within topics, and most where they started lowest.** Analyses 02 and 03 show the rise came from within topics. Analysis 04 shows Technical help rose most and Writing least, so the topics moved closer together. Together, these fit women catching up in how they use ChatGPT, not just changing what they use it for.

**2. The mix changed a lot, but the effects cancelled out.** Writing roughly halved as a share of messages, from 34.7 % to 17.5 %. That pulled women's share down, while the fall in Technical help pulled it up. Analysis 02 could only put an upper limit on the mix effect. Analysis 03 measured it and confirmed the limit held.

**3. Jobs set the level, but not the change.** In analysis 06, 2025 employment gives a share expected from jobs of 49.18 %, the same number analysis 01 found by another route. That share moved only 0.08 points from 2024 to 2025, while the observed share rose about 10 points. The observed share reached about this level in late 2025, and analysis 05 shows the rise slowed soon after. This fits women's share settling where their jobs would put it. It is not tested, and the two numbers cover different messages: work messages for the share expected from jobs, against all messages for the observed share.

**4. The remaining topic gaps mostly reflect jobs.** Technical help is still 15 points below the total (analysis 04). But analysis 01 finds that women send 34 % of technical help messages, against 33 % expected from jobs. Women do less technical work in their jobs, and their share of messages matches that. Practical guidance is the exception. It is 4.5 points below what is expected from jobs in analysis 01, and its rise slowed most in analysis 05.

## Implications

- **The fast convergence came from use, not jobs.** That points to adoption and habits, the kinds of change that can happen quickly.
- **In technical help, women's share may not rise much further unless the job mix changes.** Women already send about as large a share of technical help messages (34 %) as their share of the technical work in their jobs (33 %). A further rise there would need more women in technical jobs.
- **Method choices matter.** The topic weights in analysis 01, and the windows used in analyses 02 to 05, move results by up to a few points. Reporting more than one version guards against this.

## Weaknesses

1. **Only individual ChatGPT accounts.** Business accounts, Codex and other AI tools are excluded. If men moved work there, women's share would rise without women changing anything.
2. **Gender comes from first names,** and only names that are typically male or female.
3. **Shares, not counts.** We cannot tell whether more women started using ChatGPT or the same women used it more.
4. **Withheld and noisy data.** OpenAI withholds values based on fewer than 100 messages and adds privacy noise. No analysis has confidence intervals.
5. **Modelled job use.** The share expected from jobs uses task lists for US jobs and assumes women and men in the same job do the same tasks.
6. **Short series.** There are 27 months, and only two full years.

## Possible next steps

- **Compare Norway with other countries** using OpenAI's country files, to see whether the rise is global.
- **Use SSB's survey on generative AI by gender** to separate more users from more use.
