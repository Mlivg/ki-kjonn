# Catching up within topics or a shifting topic mix?

Script: `scripts/02_shift_share.py`. Data: `norway_gender_topics_monthly.csv` and `topics_expected_observed_persons.csv` in `data/raw`. Table: `output/02_shift_share.csv`. Figure: `output/02_shift_share.svg`. Run with `python3 -I scripts/02_shift_share.py`.

## Question

Women's share of ChatGPT messages in Norway rose from 35.1 % in July 2024 to 48.6 % in September 2026. The page on [kiindeksen.no](https://kiindeksen.no/kjonn.html) shows the rise but does not say what drives it. There are two candidates:

1. **Within topics.** Women send a larger share of the messages inside each topic.
2. **Topic mix.** Use shifts toward topics where women already send a large share.

## Result

Most of the rise happened within topics. The main comparison uses the first and last 3 months, which also avoids reading too much into one low starting month. On that comparison the total rose 10.43 points. With the topic mix held fixed, four topics give a rise of 10.51 points. That leaves −0.07 points for the mix.

| Topic | Weight | First 3 months | Last 3 months | Rise (points) |
|---|---|---|---|---|
| Technical help | 0.096 | 20.4 % | 34.5 % | 14.1 |
| Practical guidance | 0.251 | 38.4 % | 52.0 % | 13.6 |
| Seeking information | 0.133 | 32.1 % | 42.7 % | 10.6 |
| Writing | 0.382 | 49.8 % | 57.3 % | 7.5 |
| **All messages (`Alle`)** | | **39.1 %** | **49.5 %** | **10.4** |

An exact split is not possible with these files, because they do not include the monthly topic mix. Analysis 03 uses OpenAI's published monthly mix. A firmer statement comes from the range. Any fixed weights on these four topics must give a rise between 7.5 and 14.1 points. So the mix can account for at most 2.93 of the 10.43 points on the main comparison. Across all the tests below, that upper limit is never above 3.63 points.

![Women's share of messages by topic and in total, with the fixed-mix line](02_shift_share.svg)

## Method

The total share is a weighted average of the topics: each topic's share of messages times women's share in that topic, summed over topics. A rise can come from either part.

1. For each topic, take women's share in the first and last 3 months. Months OpenAI withheld are skipped.
2. Multiply each topic's rise by a fixed weight, `topic_share_work_openai`, and add them up. The weights are rescaled to sum to 1 across the four topics. This is the rise with the mix held fixed.
3. Subtract that from the rise in `Alle`. The remainder is the part left for the mix.
4. Report the lowest and highest topic rise. A weighted average cannot fall outside them, so this range holds for any fixed weights.

We do not know the true weights. The usual split weights the rises by a start mix, an end mix or an average of both. All of those fall inside the range.

Only four topics are used in the main result. Multimedia has one value in the first 3 months. Self-expression and Other/Unknown have none.

## Tests of the choices

All numbers are percentage points, except the share column.

| Test | Actual rise | Fixed-mix rise | Left for mix | Fixed mix as share of rise | Lowest topic rise | Highest topic rise | Most the mix can explain |
|---|---|---|---|---|---|---|---|
| Main | 10.43 | 10.51 | −0.07 | 100.7 % | 7.50 | 14.13 | 2.93 |
| Weights from the activity key | 10.43 | 10.46 | −0.02 | 100.2 % | 7.50 | 14.13 | 2.93 |
| Gaps filled on a straight line | 10.43 | 10.29 | 0.15 | 98.6 % | 7.12 | 13.68 | 3.32 |
| Only months with all four topics | 11.73 | 11.42 | 0.32 | 97.3 % | 8.10 | 16.03 | 3.63 |
| First and last 6 months | 9.60 | 8.68 | 0.92 | 90.4 % | 6.00 | 12.60 | 3.60 |
| First and last 12 months | 7.20 | 6.69 | 0.51 | 92.9 % | 5.21 | 9.54 | 1.99 |
| July 2024 and September 2026 only | 13.50 | 14.65 | −1.15 | 108.5 % | 10.30 | 20.10 | 3.20 |
| All seven topics, gaps filled | 10.43 | 10.24 | 0.20 | 98.1 % | not used | not used | not used |

The actual rise differs between rows because longer windows compare periods that lie closer together in time. The share of the rise held by the fixed mix stays between 90 % and 109 %.

A negative value in "left for mix" does not mean the mix pulled the total down. Differences this small can also come from the other limits below.

## Limits

1. **The mix effect is not measured.** It is what remains after the within-topic part, so it also contains any measurement difference.
2. **The weights describe work messages.** `Alle` and the topic shares cover all messages. Using the range reduces this problem for the four topics, but does not remove it for the three left out.
3. **Three topics are left out of the main result.** They hold 13.9 % of the work weights. If they had not risen at all, the fixed-mix rise would be 9.05 points. Their weights among all messages are not in these files, so they could be larger than this.
4. **The seven-topic test understates late-starting topics.** A topic with no early value starts from its first published value, which removes its earlier rise.
5. **The end of the series is thin.** In the main comparison, Technical help has one value in the last 3 months and Writing has two. The test with only complete months uses three each. OpenAI does not say why months are withheld in the files here. If withholding depends on the number of messages, the published months are not a random selection.
6. **There is no statistical uncertainty here.** Message counts per cell are not published, so the tests show how far the choices move the result. They are not confidence intervals.
7. **The level differs by about 1.3 to 1.4 points.** The fixed-mix line sits +1.41 points above `Alle` in the first 3 months and +1.27 points in the last 3. Across single months the difference runs from −0.81 to +2.51 points. The rises are comparable. The levels are not.

## What the result does not show

1. **Why women's share rose within topics.** It could be more women using ChatGPT, or the same women sending more messages. The files have no user counts.
2. **That the gap has closed everywhere.** In the last 3 months, women send 57.3 % of Writing and 34.5 % of Technical help messages.
3. **That the two explanations are separate causes.** New female users who write a lot would raise both parts. A mix effect would therefore not prove that women did not change their behaviour.
4. **That this holds for all use in Norway.** The sample covers individual subscriptions, without business accounts or Codex. Gender comes from first names, not from the users themselves.

## Checks

1. The script runs tests on made-up data before it reads the real files. The tests cover a case with both effects, a pure mix case and a pure within-topic case. They also cover the range, the gap rules and a topic that drops out.
2. Deliberate bugs were put into copies of the script, one at a time. The tests stopped eight of nine. The ninth ignored the weights, and it got through because the first test has equal rises in every topic. A new test with unequal rises now stops it.
3. The main result was recomputed in a separate short script with no shared functions. It gave 10.51 and 10.43 points.
4. A clean copy with only the script and `data/raw` gave byte-identical output. The files in `data/raw` are unchanged.

## Not checked

1. The actual topic mix per month. It is not in the files used here.
2. Topic weights across all messages, as opposed to work messages.
3. Why OpenAI withholds specific months.
