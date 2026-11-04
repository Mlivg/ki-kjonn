# Session log

## 2026-11-03

- Task: set up the project and download the data from kiindeksen.no/kjonn.html.
- Owner: asked for the folder "KI index kjønn" with the AGENTS template.
- Result: created AGENTS.md from templates/AGENTS-template.md, CLAUDE.md, README.md, this log, and the folders data/raw, scripts and output. Six files from kiindeksen.no/data/openai_signals/ saved unchanged in data/raw. No analysis run yet.

- Task: tidy the folder after the session moved here.
- Owner: approved deleting the duplicates.
- Result: deleted six byte-identical copies in data/ (checked with cmp first). Moved raw/kjonn.html to data/raw/kjonn.html and removed the empty raw/ folder. README.md updated.

- Task: replace AGENTS.md.
- Owner: asked to use the same AGENTS.md as in the templates folder.
- Result: AGENTS.md is now an unchanged copy of templates/AGENTS-template.md, with the placeholders not filled in. The filled-in version was overwritten.

- Task: fill in AGENTS.md for the research assistant goal.
- Owner: asked to make AGENTS.md fit the goal of a research assistant position and Andreas Kostøl's email.
- Result: filled the placeholders in the template copy. Tasks are reproduce the page's numbers, review code line by line, and run new analyses. Checked that Python 3.9.6 is present and pandas, numpy and matplotlib are not.

## 2026-11-04

- Task: replicate the headline numbers on kiindeksen.no/kjonn.html (expected 50 % vs observed 50 %).
- Owner: asked for a step-by-step replication from the CSVs, with every line checked and discrepancies reported.
- Result: wrote scripts/01_replicate_headline.py (standard library only). All 13 page numbers match when rounded. Expected 50.358 %, observed 50.364 %, using OpenAI's topic shares as weights. With the activity-key weights, both are about 49.2 to 49.4 %. Discrepancies: the page mixes the two weights (multimedia 4 % vs 5.9 %), practical guidance has a 4.5-point gap that the page does not mention, and the data dictionary's 49.4 matches the other weighting. Expected per topic could not be rebuilt because the activity-to-topic key is not in data/raw. Notes in output/01_replicate_headline_notes.md.

- Task: line-by-line review of scripts/01_replicate_headline.py.
- Owner: asked that every line be checked.
- Result: replaced Python's round() with round-half-up, because round(50.5) gives 50. No result changed. Added a printout of expected vs observed at three decimals and each topic's contribution to the gap. Recorded three assumptions in the notes: weights normalised by their sum (1.00017), monthly means unweighted, and SSB persons 2025 (incl. code 0000) used as totals in the activity-level check.

- Task: confirm that no CSV file was edited.
- Owner: asked whether any CSV had been changed.
- Result: downloaded the six files again from kiindeksen.no/data/openai_signals/ and compared with cmp. All six in data/raw are byte-identical to the live files. Timestamps unchanged since 2026-11-03 21:37. The only CSV created is output/01_replicate_headline.csv.

- Task: rule for raw data.
- Owner: said the files in data/raw must never be changed.
- Result: rule noted. It matches AGENTS.md ("Keep raw data and source documents unchanged"). Offered to make the files read-only with chmod a-w. Not done, waiting for the owner.

- Open points: the professor's name (Andreas Kostøl) is inferred from the page and the data dictionary, not confirmed by the owner. The activity-to-topic key is needed to rebuild expected per topic. Candidate sources: github.com/andreaskostol/AI-Norway or the OpenAI Signals download. Not checked.

- Task: make an index for the GitHub repository github.com/Mlivg/ki-kjonn.
- Owner: asked for an index for the repository.
- Result: checked the repository. It has one commit with a README containing only the heading "ki-kjonn". The local folder is not a git repository yet. Rewrote README.md as the index: result table, six findings, not checked, how to rerun, file list, data and licence, how it was made, folder context. Numbers taken from a rerun of scripts/01_replicate_headline.py in this session. The professor is not named, since the name is not confirmed. Nothing pushed.

- Task: check the repository after the owner's upload.
- Owner: uploaded files through the GitHub web page (commit ae9d7ed, 2026-11-04 12:03).
- Result: the repository holds README.md, 01_replicate_headline.csv and 01_replicate_headline_notes.md, all byte-identical to the local files. They sit in the top folder, not in output/. The script, data/raw, session-log.md, AGENTS.md and CLAUDE.md are not uploaded. Six of the README's links therefore point to missing paths, and the rerun command cannot work. The README with the local path is now public.

- Task: push the project to github.com/Mlivg/ki-kjonn with git.
- Owner: asked to push with git.
- Result: removed the local path from README.md. Added .gitignore (.DS_Store, data/raw/kjonn.html, __pycache__). Linked the folder to the repository on top of the owner's upload commit. The two result files moved from the top folder to output/. Added the script, data/raw (six files, unchanged), AGENTS.md, CLAUDE.md and this log. The old README with the local path stays in the history of commit ae9d7ed.

- Task: check the repository after the owner's second upload.
- Owner: chose to upload through the GitHub web page instead of git push (commit 117905e, 2026-11-04 12:16).
- Result: the upload added 01_replicate_headline.py, identical to the local script, in the top folder. GitHub now has four files, all in the top folder. Still missing: output/, scripts/, data/raw, AGENTS.md, CLAUDE.md, session-log.md. The README on GitHub is the old version with the local path. The script cannot run from the top folder, because it looks for data/raw one level above itself. Local commit 915f686 is not pushed, and the local folder is not changed.
