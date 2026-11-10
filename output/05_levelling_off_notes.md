# Has the rise levelled off?

Script: `scripts/05_levelling_off.py`. Tables: `output/05_levelling_off.csv` and `output/05_levelling_off_monthly.csv`. Figure: `output/05_levelling_off.svg`. Data: `norway_gender_topics_monthly.csv` in `data/raw`. Run with `python3 -I scripts/05_levelling_off.py`.

## Question

Women's share of ChatGPT messages in Norway rose from about 39 % to about 50 % between mid-2024 and autumn 2026. Is it still rising, or has it stopped?

## Result

The rise slowed sharply in the second year. It has not clearly stopped.

| July to September | Women's share | Rise from a year earlier |
|---|---|---|
| 2024 | 39.07 % | |
| 2025 | 47.40 % | +8.33 points |
| 2026 | 49.50 % | +2.10 points |

The second year's rise is 25.2 % of the first year's. The comparison uses the same three months each year, so seasonal patterns do not affect it.

![Women's share over time, and the change from a year earlier](05_levelling_off.svg)

The slowdown started in spring 2026. Compared with the same months a year earlier, the 3-month average was 6.57 to 8.33 points higher in every month from September 2025 to March 2026. After that the difference fell, to +3.57 in June and +2.10 in September 2026. The 3-month average peaked at 51.67 % for January to March 2026, and was 49.50 % for July to September 2026.

## Method

1. **Main measure, fixed before the first run:** the average of July, August and September in 2024, 2025 and 2026, and the rise from each year to the next.
2. **Change from a year earlier:** for each month from September 2025, the 3-month average ending that month minus the same 3 months a year earlier. September 2025 is the first month with a full year of data before it.
3. **Straight-line trend in each year:** the slope from July 2024 to June 2025, and from July 2025 to June 2026.

## Tests of the choices

| Version | 2024 | 2025 | 2026 | First year | Second year |
|---|---|---|---|---|---|
| Main: July to September | 39.07 | 47.40 | 49.50 | +8.33 | +2.10 |
| July only | 35.10 | 47.10 | 49.60 | +12.00 | +2.50 |
| September only | 41.60 | 49.20 | 48.60 | +7.60 | −0.60 |

The slowdown appears with both single months. With September alone, the share fell slightly in the second year.

The straight-line trend was +10.98 points per year from July 2024 to June 2025, and +5.61 from July 2025 to June 2026. That trend is still positive in the second year, because the share rose until March 2026 and then fell back.

The plan also included 6-month windows. With 27 months, there is no way to compare the same 6 calendar months in three years, so the yearly trends are used instead.

## By topic

| Topic | First year | Second year | Values used, 2024 + 2025 + 2026 |
|---|---|---|---|
| Practical guidance | +12.17 | +1.47 | 3 + 3 + 3 |
| Seeking information | +8.73 | +1.90 | 3 + 3 + 3 |
| Writing | +4.37 | +3.13 | 3 + 3 + 2 |
| Technical help | +7.58 | +6.55 | 3 + 2 + 1 |

The slowdown is clearest in Practical guidance and Seeking information. Writing and Technical help kept rising at a similar pace. Technical help's 2026 value rests on September alone, so its second-year rise is uncertain.

## Limits

1. **There are only two years to compare.** "Slowed" describes these data. It is not a statistical test, and it does not predict what happens next.
2. **Single months are noisy.** The share was 53.0 % in March 2026 and 48.6 % in September 2026. A pause and a temporary dip can look the same for a few months.
3. **There is no statistical uncertainty here.** Message counts are not published, so the tests show how far the choices move the result. They are not confidence intervals.

## What the result does not show

1. **Why the rise slowed.** One possibility is that women's share has reached about where their jobs would put it. The KI-indeksen page finds that jobs imply 50 % for work messages. This analysis cannot test that link.
2. **Whether women use ChatGPT less.** The data gives shares, not counts. A slower rise in the share is compatible with both women and men using ChatGPT more.
3. **That this holds for all AI use in Norway.** The data covers individual ChatGPT accounts only. Gender comes from first names.

## Checks

1. The script runs tests on made-up data before it reads the real file. They cover the yearly rises, gaps, the trend and the change from a year earlier.
2. Six deliberate bugs were put into copies of the script, one at a time. The tests stopped all six.
3. The main numbers were recomputed in a separate short script with no shared functions. It gave 39.07, 47.40 and 49.50, rises of 8.33 and 2.10, and the same changes from a year earlier.
4. A clean copy with only the script and `data/raw` gave byte-identical output. The files in `data/raw` are unchanged.
