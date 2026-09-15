# Results and limitations

The best confirmed **public leaderboard score was 0.88304** in the [CUHK-X Large Model Track](https://www.kaggle.com/competitions/cuhk-x-competition-large-model-track). A live observation on **15 September 2026, approximately 19:34 UTC**, showed **public rank 24 of 213 teams** and 27 team entries. This is a dated public snapshot, **not a final rank**. A private leaderboard result was unavailable at that observation.

The contribution is an audited sequence of multimodal prediction improvements and evaluation tools. It is **not a fully reproducible, independently trained end-to-end winning solution**. The submission retained part of an attributed public prediction baseline whose original generator was unavailable.

## Verified score progression

This is a curated progression, not a list of every submission. “Changed” means answers changed relative to that submission's parent. Scores are competition public scores; TRAIN counts below are separate development measurements.

| Milestone | Public score | Changed | Development evidence and decision |
|---|---:|---:|---|
| Published Fususu / `phuongncn` starting artifact | 0.77777 | — | Third-party prediction vector; credited, not claimed as this project's model |
| Audited project snapshot before the five extensions below | 0.85380 | — | Reference point; preceding work is not reconstructed by this table |
| Action-bundle MULTI transfer | 0.86549 | 6 | 11/13 against local controls 4/13 and 7/13; fixed gate passed |
| Action-bundle COMBINATION transfer | 0.87134 | 4 | 27/28 against 22/28 and 24/28; fixed gate passed |
| Second-quarter non-sequence MULTI transfer | 0.87426 | 4 | 35/37 against 30/37 and 29/37; five/six fixes, no breaks; fixed gate passed |
| HARn SINGLE transfer over all 51 eligible questions | 0.88011 | 9 | 31/34 against 32/34 and 28/34; original gate failed; separately documented exploratory submission |
| Direct whole-context ORDER over all 39 questions | **0.88304** | 5 | 26/36 against 24/36; four fixes, two breaks; stricter gates failed; separately documented exploratory submission |

The five confirmed extensions increased the public score by **0.02924** from the 0.85380 reference. Positive public scores did not retroactively pass failed TRAIN gates. The local controls are not recovered TRAIN evaluations of every inherited predictor in the submitted CSV.

The best submission has 682 ordered rows. Its final ORDER overlay changed five answers and preserved all 643 non-ORDER lines byte-for-byte. Saved-response reconstruction and a fresh-process CSV replay verified inverse option mappings and exact output bytes. The preserved best artifact's SHA256 is:

```text
db04ccbb395c81a8c88dd480b2995ca2242ef1620af7c47fee504707c0f63e45
```

Machine-readable observations are in [leaderboard_history.json](../results/leaderboard_history.json).

## Informative negative results

| Experiment | Result | What it established |
|---|---|---|
| Matched recording-level objective | 78/253 versus 80/253 for mean window loss and 134/253 for the stronger local control | Changing loss aggregation alone did not help. Initialization, windows, optimizer and training updates were matched; saved-model replay reproduced all 1,012 answers. |
| Conservative skeleton detection-order correction | Six refits: 425/809 and 430/809 versus 427/809 and 430/809. Existing weights with corrected inputs: 427/809 and 429/809. | A real preprocessing defect need not yield an accuracy gain. Original caches were reproduced before correcting clear list-order swaps; semantic actor identity remained uncertain. |
| Question-blind physical descriptions plus a fixed decoder | 25/90 and 24/90 versus local controls 51/90 and 49/90; lexical controls 28/90 and 22/90 | All 90 observations completed, but the representation did not beat the stronger reference. All 540 held predictions from 18 saved heads replayed exactly. |
| Higher-reasoning, reversed-label ORDER consensus | 26/36 versus direct 26/36; one fix, one break; each higher-reasoning arm 25/36 | More reasoning and label agreement did not improve this cohort. All 72 calls completed; the fixed gate failed, so no TEST inference or submission followed. |

STANDARD and STRESS are two evaluation partitions over the same population, not independent datasets. These studies reused previously examined development people and questions. Their gates controlled decisions within this project; they do not establish untouched-holdout generalization or statistical significance for leaderboard gains.

## Reproducibility boundary

- **Reproducible here:** the published small utilities and synthetic examples, with their tests. See the code map for their scope.
- **Verified in the private experiment archive:** hashes, saved-model or saved-response replay, complete prediction commitments before grading, token/deadline accounting, and protected-row CSV assembly. Those artifacts are not redistributed here.
- **Not recoverable as a complete fresh-input system:** the inherited MANNER generator. All 144 MANNER answers in the best submission retained the public baseline. Recorded ownership also leaves 20 inherited HARn OBJECT answers; the remaining HARn OBJECT answer came from an older local overlay. The local MANNER 427/430 reference is a proxy, not that inherited generator.
- Hosted-model versions, access, benchmark media, private caches and saved responses are additional requirements for reproducing the historical experiments. Replaying saved outputs proves consistency with those outputs, not deterministic regeneration from new recordings.

No private-score improvement, final placement, leaderboard win, or complete fresh-input reproduction is claimed. See [ATTRIBUTION.md](ATTRIBUTION.md) for upstream credit and release boundaries.
