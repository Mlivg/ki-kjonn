# Replication of the headline numbers on kiindeksen.no/kjonn.html

Script: `scripts/01_replicate_headline.py`. Data: the six files in `data/raw`, downloaded 2026-11-03. Table: `output/01_replicate_headline.csv`. Run with `python3 -I scripts/01_replicate_headline.py`.

## Result

All 13 numbers on the page round to the same whole percent in our calculation.

| Number on the page | Page | Ours | Source |
|---|---|---|---|
| Women's share of the employed | 47 | 47.35 | SSB 12542, 2025, all codes |
| Expected, all work messages | 50 | 50.36 | topics file, persons |
| Observed, all work messages | 50 | 50.36 | topics file |
| Expected, three job counts | 49, 50, 51 | 49.38, 50.36, 50.78 | fte, persons, relationships |
| Writing, observed / expected | 57 / 55 | 56.69 / 54.71 | topics file |
| Technical help, observed / expected | 34 / 33 | 34.09 / 33.15 | topics file |
| Multimedia, observed / expected | 46 / 32 | 46.01 / 32.42 | topics file |
| Multimedia share of work messages | 4 | 4.03 | `share_of_work_messages` |

At three decimals the expected share is 50.358 % and the observed share is 50.364 %.

## Method choices that decide the result

1. **Topic weights.** The topics file has two weight columns. The page's 50 vs 50 comes only from `topic_share_work_openai`, the topic shares OpenAI reports. With `share_of_work_messages`, the shares implied by the activity key, we get 49.18 expected and 49.36 observed. The gap stays small in both cases.
2. **The 47 % includes code 0000.** That code means occupation unknown. Without it, women are 48.10 %.
3. **Observed per topic is a plain monthly mean.** Each topic's observed value equals the unweighted mean of the published months from October 2025 to September 2026. Months without a value are skipped. Multimedia and technical help have 7 of 12 months. Months with more messages get no extra weight.

## Small discrepancies

1. **Two weights in one paragraph.** The page uses OpenAI's topic shares for the 50 %. It then says multimedia is "4 prosent av arbeidsmeldingene". That 4 % comes from the other column. In OpenAI's own topic shares, multimedia is 5.9 %.
2. **"Emne for emne stemmer det også" holds only partly.** Practical guidance has 51.95 % observed against 56.42 % expected, a gap of 4.5 points. It is a quarter of work messages. It pulls the total down by 1.12 points, more than any other topic. Multimedia (+0.79) and writing (+0.76) pull it up. The total of 50 vs 50 is partly offsetting gaps, not a match in every topic.
3. **The data dictionary gives an older observed value.** It says the observed share is 49.4. That matches our 49.36 with `share_of_work_messages`, not the page's 50.
4. **The topic weights sum to 1.00017.** The script divides by this sum. Without that, both shares rise by 0.01 points.

## Not checked

1. **Expected per topic from scratch.** The activity file has no topic column, so we cannot rebuild the expected value for each topic. The key from activity to topic is not in the downloaded files. It may be in the OpenAI download or in the AI-Norway repository.
2. **One open question.** Weighting each activity's women's share by its ChatGPT share gives 48.14 % expected, not 49.18 %. The two would be equal if each topic's expected value were a ChatGPT-share-weighted mean of its activities. One explanation is that the topic values weight activities by working time instead. Another is that a different employment total was used. Without the topic key we cannot tell which.
3. The `ratio` column in the activity file. Our first attempt gives 3.443 against 3.433 in the file for one activity. The exact definition is not confirmed.
