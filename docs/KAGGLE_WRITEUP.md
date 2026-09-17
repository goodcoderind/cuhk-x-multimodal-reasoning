# 0.88304 public score: code, consistent decoding and experiment notes

I am sharing the code and a technical report from my CUHK-X Large Model Track work:

**[GitHub repository — cuhk-x-multimodal-reasoning](https://github.com/goodcoderind/cuhk-x-multimodal-reasoning)**

The best recorded public score is **0.88304**. On 15 September 2026, approximately 19:34 UTC, the public leaderboard showed Obro at **24/213 teams**. This is a dated public snapshot; a final private result was not available at that observation.

## Credit and scope

The starting point was **Fususu / phuongncn's [public 0.77777 prediction baseline](https://www.kaggle.com/code/phuongncn/lb-0-77777-exact-submission-research-handoff)**. Some inherited predictions remain, including all 144 MANNER answers. The repository publishes selected original components and a report; it does not reproduce the complete 0.88304 submission from raw media. Development and experiment operations were AI-assisted.

## What was useful

- **Frame preparation:** split four-frame contact sheets and square-pad each frame before frozen CLIP encoding. A square center crop of a wide sheet can discard relevant events.
- **Cross-question consistency:** jointly score candidate action sets and related single/multi/combination answers about the same recording.
- **Task-specific evaluation:** evaluate targeted vision-model approaches separately for action bundles, object/action questions, and temporal ordering.
- **Validation and release checks:** use person-based partitions, remap permuted choices and temporal anchors, replay committed outputs, and verify that overlays preserve unrelated submission rows.

Selected public milestones were **0.85380 → 0.86549 → 0.87134 → 0.87426 → 0.88011 → 0.88304**. The [results report](https://github.com/goodcoderind/cuhk-x-multimodal-reasoning/blob/main/docs/RESULTS.md) explains the development controls and distinguishes passed gates from exploratory submissions after failed gates. These are public observations, not isolated causal estimates or private-score guarantees.

## What did not transfer

Frozen V-JEPA 2 features, physical-description intermediates, and additional reasoning were evaluated rather than assumed to help. The final higher-reasoning ORDER consensus completed 72 calls on 36 TRAIN recordings and tied the direct method at **26/36**, with one fix and one new error. It was not submitted. A pose audit also found a genuine input-processing problem, but correcting it did not establish an accuracy gain.

## Try the code

The MIT-licensed package includes the joint decoder, grouped-holdout checks, strict option remapping, tests, and an offline synthetic demo. It needs no competition data, API key, or accelerator. An optional frame encoder uses a separately supplied local checkpoint.

The examples contain invented inputs. No competition data, answer keys, prediction CSVs, model weights, or private provider records are redistributed. The [reproducibility notes](https://github.com/goodcoderind/cuhk-x-multimodal-reasoning/blob/main/docs/REPRODUCIBILITY.md) and [attribution](https://github.com/goodcoderind/cuhk-x-multimodal-reasoning/blob/main/docs/ATTRIBUTION.md) describe the exact boundary.

I hope the decoder, preprocessing lessons, and negative results are useful to others working on multimodal action understanding.
