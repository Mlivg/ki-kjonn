# The rise in women's share, split with the measured topic mix

Script: `scripts/03_measured_mix.py`. Tables: `output/03_measured_mix.csv` and `output/03_measured_mix_topics.csv`. Figure: `output/03_measured_mix.svg`. Data: `norway_gender_topics_monthly.csv` in `data/raw`, and OpenAI's files in `data/raw_openai_signals`. Run with `python3 -I scripts/03_measured_mix.py`.

## Question

Analysis 02 did not have each topic's share of messages per month, so it could only treat the mix effect as what remained. OpenAI's Signals download has that share for Norway, for all 27 months and all seven topics. This analysis measures both parts directly.

## Result

Most of the rise happened within topics, and the topic mix explains almost none of it. From the first 3 to the last 3 months, the total rose 10.43 points.

| Part | Points |
|---|---|
| Within topics | +10.56 |
| Topic mix | −0.74 |
| Not explained | +0.61 |
| **Actual rise** | **+10.43** |

![Topic mix over time and the split of the rise](03_measured_mix.svg)

The topic mix did change a lot. Writing fell from 34.7 % to 17.5 % of messages. The mix effect is still small, because the shifts pull in opposite directions.

| Topic | Share of messages, start | End | Women's share, start | End | Within | Mix |
|---|---|---|---|---|---|---|
| Writing | 34.7 % | 17.5 % | 49.8 % | 57.3 % | +1.96 | −1.65 |
| Practical guidance | 24.4 % | 29.8 % | 38.4 % | 52.0 % | +3.69 | +0.07 |
| Seeking information | 19.1 % | 26.8 % | 32.1 % | 42.7 % | +2.44 | −0.50 |
| Technical help | 11.9 % | 4.7 % | 20.4 % | 34.5 % | +1.17 | +1.20 |
| Multimedia | 3.5 % | 5.9 % | 26.8 % | 37.8 % | +0.52 | −0.28 |
| Self-expression | 3.5 % | 8.6 % | 45.9 % | 53.0 % | +0.43 | +0.28 |
| Other/unknown | 3.0 % | 6.8 % | 44.2 % | 51.4 % | +0.35 | +0.15 |

Women's share is high in Writing, so its fall lowers the total by 1.65 points. Women's share is low in Technical help, so its fall raises the total by 1.20 points.

The results are consistent with women catching up in their use of individual ChatGPT accounts in Norway. Women's share rose in all four topics we can follow from the start. Technical help started lowest and rose most, while Writing started highest and rose least. The data cannot show whether women are catching up in AI use overall, because business accounts, Codex and other AI tools are not included.

## Method

The total share is the sum over topics of each topic's share of messages times women's share in that topic. For each topic:

- **Within** = average share of messages × change in women's share.
- **Mix** = (average women's share − average total) × change in share of messages.

Averages are taken over the start and end periods. The two parts then add up exactly to the change in the rebuilt total, with no interaction term. Subtracting the average total leaves the sum unchanged, because the changes in topic shares sum to zero. It gives each topic's mix part the right sign. A low-share topic that shrinks pushes women's share up.

**Not explained** is the actual rise in `Alle` minus the two parts.

Each month's topic shares are rescaled to sum to 1, because rounding leaves them between 0.998 and 1.001. A topic with no value in a window takes its nearest published value. This applies to Self-expression and Other/Unknown in the first 3 months.

## Do the files fit together?

This was checked before the split, against a limit of 1 point set before the first run. In the 6 months where all seven topics have values, the rebuilt total differs from `Alle` by 0.26 points on average, in absolute terms. The largest difference is −0.51 points.

| Month | Rebuilt | Published | Difference |
|---|---|---|---|
| 2025-09 | 49.25 | 49.20 | +0.05 |
| 2025-10 | 47.36 | 47.10 | +0.26 |
| 2025-11 | 50.56 | 50.40 | +0.16 |
| 2026-01 | 50.94 | 51.20 | −0.26 |
| 2026-03 | 52.49 | 53.00 | −0.51 |
| 2026-09 | 48.25 | 48.60 | −0.35 |

## Tests of the choices

All numbers are percentage points, except the share column.

| Version | Actual rise | Within | Mix | Not explained | Within as share of rise |
|---|---|---|---|---|---|
| Main | 10.43 | 10.56 | −0.74 | 0.61 | 101.2 % |
| First and last 6 months | 9.60 | 9.07 | 0.07 | 0.46 | 94.5 % |
| First and last 12 months | 7.20 | 6.64 | 0.19 | 0.38 | 92.2 % |
| July 2024 and September 2026 only | 13.50 | 14.06 | −0.73 | 0.17 | 104.2 % |
| Only the four topics with early values | 10.43 | 10.99 | −1.06 | 0.50 | 105.3 % |
| Gaps filled on a straight line | 10.43 | 10.67 | −0.61 | 0.38 | 102.2 % |
| Topic mix of work messages | 10.43 | 10.40 | 0.57 | −0.54 | 99.7 % |

Across these versions the mix stays between −1.06 and +0.57 points. All seven topics have real values in the 12-month windows, so that version needs no nearest values. The four-topic version and the work-message version compare with the total for all messages, so their "not explained" column is less meaningful.

### What if the thin topics started elsewhere?

Multimedia, Self-expression and Other/Unknown have little or no early data. They held about 10 % of messages at the start. These tests move all three of their start shares together.

| Assumption about their start shares | Within | Mix | Not explained | Rebuilt start (published 39.07) |
|---|---|---|---|---|
| Main | 10.56 | −0.74 | 0.61 | 39.03 |
| 10 points lower | 12.12 | −1.30 | −0.38 | 38.03 |
| 10 points higher | 8.99 | −0.17 | 1.61 | 40.02 |
| 20 points lower | 13.68 | −1.87 | −1.37 | 37.04 |
| Extreme: all at 0 % | 16.74 | −3.08 | −3.23 | 35.19 |
| Extreme: all at 100 % | 1.13 | 2.60 | 6.70 | 45.12 |

The extreme of 100 % would reverse the conclusion. The published total rules it out, because the rebuilt start would then be 6.05 points above the published value. The nearest values give a rebuilt start of 39.03 against 39.07. The total limits the average of the three topics' start shares, not each one separately.

## Comparison with analysis 02

Analysis 02's conclusion holds. It found a fixed-mix rise of 10.51 points and an upper limit of 2.93 points for the mix on the same windows. This analysis measures +10.56 and −0.74.

1. **The closeness of 10.51 and 10.56 is partly luck.** Analysis 02's work weights gave Writing 38.2 %, while its average share of all messages here is about 26 %. Analysis 02 also left out three topics.
2. **Analysis 02's −0.07 was not a measured mix effect.** It combined the mix with what this analysis reports as not explained.

The three left-out topics make up about 21 % of messages at the end of the period, against 13.9 % of the work weights. Analysis 02 noted that their weights could be larger, and they are.

## Limits

1. **The withheld topic cells remain.** The new file adds the mix, not the women's shares. All 149 women's shares in our monthly file equal OpenAI's. OpenAI publishes a cell only if its effective number of messages is at least 100, so the gaps are linked to low message counts and are not random.
2. **The two measures cover slightly different messages.** The topic mix covers all messages. Women's share counts only names that are typically feminine or masculine. The fit check shows the effect is small, but the difference may drift over time. In the 6 complete months, the rebuilt total goes from above the published total to below it. With gaps filled, the mean difference is +0.18 points in the first 9 months, −0.01 in the middle 9 and −0.36 in the last 9. This drift is about the size of the "not explained" part. The cause is not checked.
3. **The numbers contain noise.** OpenAI adds differential privacy noise and rounds to three decimals. Norway's numbers rest on a part of a global sample of 1 million messages per month.
4. **There is no statistical uncertainty here.** The files do not give message counts, so the tests show how far the choices move the result. They are not confidence intervals.
5. **The end of the series is thin.** In the main version, four topics have one value in the last 3 months, and Writing has two. The "not explained" part mostly comes from there. It falls from 0.61 to 0.38 points when gaps are filled.

## What the result does not show

1. **Why women's share rose within topics.** It could be more women using ChatGPT, or the same women sending more messages. The files have no user counts.
2. **Why the topic mix changed.** The fall in writing could reflect changes in the product, in users or in how the classifier sorts messages. These data cannot separate them.
3. **That the two explanations are separate causes.** New female users could change both women's share and the topic mix.
4. **That the gap has closed everywhere.** In the last 3 months, women send 57.3 % of Writing and 34.5 % of Technical help messages.
5. **That this holds for all use in Norway.** The sample covers individual accounts, without business accounts or Codex. Gender comes from first names, not from the users themselves.

## Checks

1. The script runs tests on made-up data before it reads the real files. They cover unequal rises, a pure mix case, a pure within-topic case, the sign of a topic's mix part, rescaling and the gap rules.
2. Ten deliberate bugs were put into copies of the script, one at a time. The tests stopped all ten.
3. The script stops if the kiindeksen file differs from OpenAI's numbers, for the topics or the total, or if a topic-mix cell is empty.
4. The main result was recomputed in a separate short script with no shared functions. It gave 10.56, −0.74, 10.43 and 0.61.
5. A clean copy with only the script and the two data folders gave byte-identical output. The files in both data folders are unchanged.

## Not checked

1. Why Writing's share of messages fell.
2. Why the rebuilt total drifts from above to below the published total.
