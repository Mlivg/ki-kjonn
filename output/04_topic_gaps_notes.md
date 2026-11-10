# Are the gaps between topics closing?

Script: `scripts/04_topic_gaps.py`. Tables: `output/04_topic_gaps.csv` and `output/04_topic_gaps_topics.csv`. Figure: `output/04_topic_gaps.svg`. Data: `norway_gender_topics_monthly.csv` in `data/raw`. Run with `python3 -I scripts/04_topic_gaps.py`.

## Question

Women's share of ChatGPT messages differs a lot between topics. Analyses 02 and 03 showed that the total rose mainly within topics. This analysis asks whether the differences between topics also got smaller.

## Result

The gap between topics shrank. Among the four topics with early values, the gap between the highest and lowest women's share fell from 29.43 to 22.80 points, from the first to the last 3 months. Writing was the highest and Technical help the lowest at both ends, and in every one of the 21 months where all four are published.

| Topic | First 3 months | Last 3 months | Change | Distance from the total, start | Distance from the total, end |
|---|---|---|---|---|---|
| Writing | 49.8 % | 57.3 % | +7.5 | +10.7 | +7.8 |
| Practical guidance | 38.4 % | 52.0 % | +13.6 | −0.7 | +2.5 |
| Seeking information | 32.1 % | 42.7 % | +10.6 | −7.0 | −6.8 |
| Technical help | 20.4 % | 34.5 % | +14.1 | −18.7 | −15.0 |

The gap shrank because Technical help rose almost twice as much as Writing. Technical help is still 15.0 points below the total. Seeking information stayed about 7 points below the total. Writing moved further above 50 %.

![The gap between topics, month by month](04_topic_gaps.svg)

## Method

1. For each topic, take women's share in the first and last window of months. Months OpenAI withheld are skipped.
2. **Main measure:** the highest share minus the lowest share among the four topics. This was chosen before the first run.
3. **Second measure:** the average distance from 50 %, ignoring direction.
4. **Month by month:** the same gap in each of the 21 months where all four topics are published, and a straight-line trend through them.

## Tests of the choices

All numbers are percentage points.

| Version | Gap, start | Gap, end | Change |
|---|---|---|---|
| Main: first and last 3 months | 29.43 | 22.80 | −6.63 |
| First and last 6 months | 28.38 | 21.78 | −6.60 |
| First and last 12 months | 26.93 | 22.61 | −4.33 |
| First and last 3 months with all four topics published | 29.43 | 21.50 | −7.93 |
| All seven topics, first and last 12 months | 29.51 | 26.67 | −2.83 |

The gap shrinks in every version, by between 2.83 and 7.93 points. With all seven topics, Self-expression is the highest and the gap shrinks least.

Month by month, the gap goes from 31.7 points in July 2024 to 23.1 in September 2026. The straight-line trend is −2.93 points per year. Single months swing a lot, between 12.7 and 31.7 points. The two lowest values come from months where Technical help jumped to about 40 %.

## The second measure is misleading here

The average distance from 50 % fell from 14.83 to 8.02 points. That mostly reflects the total rising toward 50 %. Writing moved away from 50 %, from 49.8 % to 57.3 %, so the distance from 50 % is not the same as the distance between topics. The main measure does not depend on the level of the total.

## Limits

1. **The end of the series is thin.** In the main version, Technical help has one value in the last 3 months and Writing has two. The version with complete months uses three each and gives a larger fall.
2. **Single months are noisy.** The data has privacy noise, and Norway's numbers rest on a small part of OpenAI's global sample. The trend line is a description, not a statistical test.
3. **There is no statistical uncertainty here.** Message counts are not published, so the tests show how far the choices move the result. They are not confidence intervals.
4. **Three topics have too little early data** for the main version. The 12-month version with all seven topics shows a smaller fall.

## What the result does not show

1. **Why the gaps shrank.** More women could be asking technical questions, or men could have moved technical work to tools outside this data, such as business accounts or Codex.
2. **That the gaps have closed.** Technical help is still 15.0 points below the total.
3. **That this holds for all AI use in Norway.** The data covers individual ChatGPT accounts only. Gender comes from first names.

## Checks

1. The script runs tests on made-up data before it reads the real file. They cover the gap, the distance from 50 %, gaps in the data and the trend.
2. Six deliberate bugs were put into copies of the script, one at a time. The tests stopped five. The sixth changed the trend formula in a way that gives the same answer, so it is not a real bug.
3. The main gaps and the trend were recomputed in a separate short script with no shared functions. It gave 29.43, 22.80 and −2.93.
4. A clean copy with only the script and `data/raw` gave byte-identical output. The files in `data/raw` are unchanged.
