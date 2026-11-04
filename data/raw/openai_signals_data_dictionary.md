# ChatGPT-bruk per yrke: OpenAI Signals v3.0 koblet til STYRK-08

Tre CSV-er med andelen arbeidsrelaterte ChatGPT-meldinger i Norge som faller
på oppgavene i hvert norske yrke. Kilden er OpenAI Signals v3.0 fra 26. oktober
2026. Lisensen er CC BY 4.0. Nedlastingssiden er
https://openai.com/signals/data-download/ og kildefilen ble hentet 27. oktober
2026. Filene her er bygget av `analysis/03_mappings/build_openai_signals_mapping.py`
i repoet github.com/andreaskostol/AI-Norway.

## Hva OpenAI publiserer

OpenAI tar et utvalg på 1 million meldinger per måned fra individuelle
ChatGPT-abonnement. Bedriftskontoer og Codex er ikke med. En språkmodell
sorterer de arbeidsrelaterte meldingene på 164 arbeidsaktiviteter fra O*NET.
Aktivitetene heter Intermediate Work Activities (IWA). Resten havner i en
samlebøtte kalt «Other IWA». Tallene er andeler per land og kvartal med
personvernstøy. De summerer til 1 for hvert land og kvartal. Norge har tall for
sju kvartaler fra første kvartal 2025 til tredje kvartal 2026.

## Koblingen til norske yrker

Hver aktivitet er en gruppe av detaljerte aktiviteter (DWA). Hver O*NET-oppgave
hører til én eller flere av dem i O*NET 30.2. Oppgavene hører til amerikanske
yrker i O*NET-SOC 2018. Derfra går kjeden via SOC 2010 og ISCO-08 til STYRK-08.
Trinnene og de manuelle kartene er de samme som for Eloundou- og Mouchel-målene
på kiindeksen.no. 397 av 407 STYRK-koder får verdi.

To forenklinger følger av kjeden. Alle oppgaver i samme aktivitet får samme
bruk fordi OpenAI måler på aktivitet og ikke på oppgave. Oppgaver som bare
hører til aktiviteter OpenAI ikke rapporterer får null bruk. Medianyrket har
59 prosent av oppgavene sine i en rapportert aktivitet.

## Filene

### styrk08_openai_signals_mapping.csv

Én rad per STYRK-08-kode. Alle sju kvartalene er slått sammen.

| Kolonne | Innhold |
|---|---|
| `styrk08` | STYRK-08-kode på fire siffer |
| `openai_no_share` | Andel av Norges arbeidsrelaterte ChatGPT-meldinger som faller på yrkets oppgaver. Hver aktivitets andel deles likt på alle par av yrke og oppgave som har aktiviteten. Summen over alle O*NET-yrker er bevart. Skala 0 til 1. |
| `openai_no_profile` | Snittet over yrkets oppgaver av aktivitetsandelen til hver oppgave. Ikke delt på antall par. Skala 0 til 1. |
| `openai_us_share` | Som `openai_no_share` med amerikanske meldinger |
| `openai_us_profile` | Som `openai_no_profile` med amerikanske meldinger |
| `coverage` | Andel av yrkets O*NET-oppgaver som hører til minst én rapportert aktivitet |
| `pctl_rank` | Persentilrang for `openai_no_share` blant de 397 yrkene. Skala 0 til 100. |
| `quintile` | Femdel etter `openai_no_share` med like mange yrker i hver. 1 er lavest og 5 høyest. |
| `n_soc_matched` | Antall SOC 2010-koder som bidrar til yrket |
| `has_partial_match` | 1 når minst én SOC-kobling er merket delvis i BLS-kryssgangen |
| `manual_map` | Kilden når yrket er koblet manuelt. Ellers tomt. |

### styrk08_openai_signals_quarterly.csv

Én rad per STYRK-08-kode og kvartal.

| Kolonne | Innhold |
|---|---|
| `styrk08` | STYRK-08-kode |
| `quarter` | Første dag i kvartalet. 2025-01-01 er første kvartal 2025. |
| `openai_no_share` | Som i mappingfilen for kvartalet alene |
| `openai_no_profile` | Som i mappingfilen for kvartalet alene |

Kvartalstallene er støyete. Rangkorrelasjonen mellom to påfølgende kvartaler
er 0,61 til 0,66 på aktivitetsnivå. Bruk den samlede filen til rangering.

### styrk08_openai_iwa_top.csv

De ti aktivitetene med størst norsk andel blant aktivitetene yrkets
oppgaver hører til. Én rad per yrke og rang.

| Kolonne | Innhold |
|---|---|
| `styrk08` | STYRK-08-kode |
| `rank` | 1 til 10 |
| `iwa` | O*NET-id for aktiviteten |
| `iwa_title` | Aktivitetens navn på engelsk |
| `share_no` | Aktivitetens andel av Norges arbeidsrelaterte meldinger over alle kvartalene |
| `share_us` | Samme for USA |
| `n_tasks_in_iwa` | Hvor mange av yrkets oppgaver som hører til aktiviteten |
| `n_tasks_occupation` | Antall oppgaver i yrket summert over O*NET-yrkene bak koden |

### iwa_titles_no.csv

De 164 aktivitetene med norsk navn oversatt for kiindeksen.no. Kolonnene er
`iwa` og `iwa_title` og `iwa_title_no`.

## Sitering

Chatterji m.fl. (2026). OpenAI Signals v3.0. OpenAI.
https://openai.com/signals/data-download/. Den fulle forfatterlista står i
README i samme mappe som byggescriptet. Koblingen til STYRK-08 er laget av
Hernæs og Kostøl for KI-indeksen på kiindeksen.no.

## Filer fra notatet om kjønn, alder og ChatGPT-bruk (28. oktober 2026)

Elleve filer til er lagt i samme mappe, fra aldersrunden og tredje kjønnsrunde
i `analysis/03_mappings/build_openai_age_expected.py` og
`build_openai_gender_exposure.py`, pluss de tre SSB-tabellene de bygger på.
Engelsk dataordbok med alle kolonnene ligger i `paper/chatgpt-gender/data/README.md`
i repoet.

| Fil | Innhold |
|---|---|
| `activities_age_norway.csv` | De 164 aktivitetene med aldersfordelingen til arbeidstiden over OpenAIs seks aldersgrupper |
| `topics_age_expected_observed.csv` | Per emne og aldersgruppe: forventet fra jobbene, observert av OpenAI, forholdstall |
| `styrk08_openai_age.csv` | Yrker med aldersfordeling og bruk per sysselsatt per aldersgruppe |
| `ssb_06161_sysselsatte_ettaarig_alder.csv` | SSB 06161, sysselsatte etter ettårig alder, 4. kvartal 2025 |
| `gender_exposure_quintiles.csv` | Kvinner og menn per Eloundou-kvintil, bruk per sysselsatt og forholdstall, rå og reveid |
| `gender_age_bands.csv` | Det samme per aldersbånd (under 40, 40-54, 55+) fra SSB 11658 |
| `styrk08_wage_growth_gender.csv` | Lønnsvekst 2025K2 til 2026K2 per kjønn og firesifret yrke, SSB 11658 |
| `wage_growth_gender_by_quintile.csv` | Sysselsettingsvektet lønnsvekst per kjønn, kvintil og aldersbånd |
| `ssb_12542_sysselsatte_yrke4_kjonn.csv` | SSB 12542, sysselsatte per yrke og kjønn, 4. kvartal 2015-2025 |
| `ssb_13311_manedslonn_yrke2_kjonn.csv` | SSB 13311, månedslønn per tosifret yrke og kjønn, 2016-2025 |
| `ssb_11658_lonnstakere_lonn_yrke4_kjonn_alder.csv` | SSB 11658, lønnstakere og månedslønn per yrke, kjønn og aldersbånd, 2023K2-2026K2 |

Fjerde kjønnsrunde (30. oktober 2026, `build_openai_gender_baselines.py`):
`gender_baselines_summary.csv`, `topics_expected_observed_persons.csv`,
`gender_exposure_quintiles_persons.csv`, `gender_age_bands_persons.csv` og
`styrk08_openai_gender_persons.csv`. Alle kjønnstall regnet på tre måter å
telle jobber på (personer fra SSB 12542, arbeidsforhold fra registeret,
heltidsekvivalenter fra SSB 11658). Notatet bruker personer. Merk at
`build_openai_gender_expected.py` skalerer kvinners arbeid til 47,4 prosent
personer, men bruker forholdstallene på registertall der kvinner er 49,0
prosent, så den justerte kvinneandelen der (51,2) gjenskaper ikke den
observerte (49,4). De nye filene gjør det.
