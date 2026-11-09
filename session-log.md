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

- Task: check the repository after the owner's third upload.
- Owner: deleted the four flat files and uploaded the project folder through the GitHub web page (commit afe89a7, 2026-11-04 12:25).
- Result: all 13 files are on GitHub with the right structure, byte-identical to the local files. kjonn.html is left out. The README has no local path. A fresh clone runs the script and gives an identical output table. One problem: everything sits inside a folder "KI index kjønn/", so GitHub shows no README on the front page. .gitignore is not uploaded. Local commit 915f686 is not pushed and no longer matches GitHub.

- Task: move the project from the folder "KI index kjønn/" to the top of the repository.
- Owner: chose to do it with git push.
- Result: based the local repository on GitHub's commit afe89a7 and committed the move, with .gitignore. The owner pushes and logs in.

- Task: check the repository after the owner moved the files by hand.
- Owner: deleted the folder "KI index kjønn/" and uploaded the files to the top of the repository through the GitHub web page (commits 268ac71 and 07a960b, 2026-11-04 12:35 to 12:36). Chose this over git push.
- Result: all 13 files are in the top folder, identical to the local files. kjonn.html is left out. All six local links in README.md resolve. A fresh clone reruns the script and gives an identical output table with no unmatched numbers. The local git repository now points to GitHub's commit 07a960b. The unpushed local commit 538111b is dropped, and no file contents changed. .gitignore exists only locally.

- Task: a simple website for the repository, as a list of analyses.
- Owner: asked for a very simple index page on github.io, with the replication as the first entry and room for later analyses.
- Result: wrote index.html in the top folder. One card for analysis 01, with the result line and links to notes, results table and script on GitHub. An HTML comment shows how to add the next analysis. Checked in the browser pane at desktop and phone width, light and dark. No horizontal scroll. Not uploaded yet. GitHub Pages must be turned on by the owner (Settings, Pages, branch main, folder /root). Expected address: https://mlivg.github.io/ki-kjonn/ (not checked).

- Task: check the live site.
- Owner: uploaded index.html (commit 0f816e2, 2026-11-04 12:47) and asked for a check.
- Result: index.html on GitHub is identical to the local file. https://mlivg.github.io/ki-kjonn/ returns 404. GitHub's API reports has_pages false, so Pages is not turned on yet. The three links in the page (notes, table, script) return 200. The owner also edited README.md on GitHub (commit 7d70dbe), so the local README.md is now older than GitHub's.

- Task: check the site after GitHub Pages was turned on.
- Owner: turned on GitHub Pages (branch main, root).
- Result: https://mlivg.github.io/ki-kjonn/ returns 200. The live page is byte-identical to the local index.html. Opened in the browser pane. The links to notes, table and script point to the right files.

- Task: sync the local folder with GitHub.
- Owner: asked to sync.
- Result: the local repository points to GitHub's latest commit (0f816e2). README.md now has the owner's edit from GitHub, which removes the sentence "Every line was then reviewed by hand." All other files match GitHub. Only session-log.md (newer entries) and .gitignore exist locally and are not on GitHub.

## 2026-11-09

- Task: analysis 02, split the rise in women's share of ChatGPT messages into a within-topic part and a topic-mix part, using only the files in data/raw.
- Owner: set the question (catching up within topics or a shifting mix), rejected two earlier plans, chose existing data only, and approved the plan.
- Result: wrote scripts/02_shift_share.py, output/02_shift_share.csv, output/02_shift_share.svg and output/02_shift_share_notes.md, and added card 02 to index.html. On the first and last 3 months the total rose 10.43 points. With a fixed mix, four topics give 10.51 points, leaving -0.07 for the mix. Across seven further tests the fixed-mix rise was 90.4 % to 108.5 % of the actual rise. Under any fixed weights on the four topics, the mix can explain at most 3.63 points. The monthly topic mix is not published, so the mix effect is not measured directly. Tests on made-up data pass and stopped five deliberate bugs. A separate recalculation of the main result and a clean-copy rerun matched. data/raw is unchanged. README.md is not updated. Nothing is uploaded to GitHub, so the new links on the card are not checked.

- Task: add analysis 02 to README.md.
- Owner: approved the update.
- Result: README.md now covers both analyses, with a section for analysis 02, a second rerun command, new file rows and the checks run. Analysis 01's sections moved under one heading. The contents row "Claude Code, checked line by line" was replaced, because the owner had removed that claim from the body text and no joint line-by-line review has been done for analysis 02. Not uploaded to GitHub.

- Task: go through scripts/02_shift_share.py line by line with the owner, part 1 of 4 (lines 1 to 100).
- Owner: asked for the walkthrough.
- Result: found one wrong comment on line 30. It said the other three topics have no values in the first three months, but Multimedia has one (September 2024). Corrected the comment. Rerun gave identical output files.

- Task: line-by-line walkthrough with the owner, part 2 of 4 (the tests, lines 103 to 163).
- Owner: asked to continue.
- Result: the review found a weak test. No test checked that the weights change the result, because the first test has equal rises in every topic. A planted bug that ignored the weights got through. Added a test with unequal rises, which now stops that bug. Four other new bugs were also tried. Three were stopped, and one (nearest fill taking the other side) behaves the same as the original code, so it is not a real bug. Rerun gave identical output files. Updated the check lines in the notes and README.md.

- Task: line-by-line walkthrough with the owner, part 3 of 4 (real data, the eight versions, the output table).
- Owner: asked to continue.
- Result: removed one check that could never fail (float() already stops on an empty total) and renamed the variable gaps to level_diff, because "gaps" means withheld months elsewhere in the script. Rerun gave identical output files.

- Task: line-by-line walkthrough with the owner, part 4 of 4 (the figure code).
- Owner: asked to continue.
- Result: the vertical scales are set by hand, and nothing stopped a value from being drawn outside a panel. Added two checks. A deliberately narrow scale now stops the script. Output files are unchanged, and a clean copy gave identical output. The walkthrough of the script is finished. Nothing is uploaded to GitHub.
