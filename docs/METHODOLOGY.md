# Methodology

This project combined frozen visual representations, supervised motion and action models, and selected hosted vision-model predictions for CUHK-X's Large Model Track. The public package preserves several useful components; it is not the complete system that generated every answer in the best submission. See [reproducibility](REPRODUCIBILITY.md) and [attribution](ATTRIBUTION.md).

## Questions, evidence and output structure

CUHK-X evaluates human action understanding and reasoning using permitted non-RGB sensing modalities. Infrared and depth-color video were important visual inputs here; skeleton and IMU supplied additional motion features. A three-channel rendering of infrared or depth is still a sensor visualization, not ordinary RGB camera footage. The challenge excludes the RGB camera modality. [Official challenge description](https://www.ubicomp.org/ubicomp-iswc-2026/cuhk-x-competition/).

Several questions can describe the same recording. A single-action answer, a multi-action set and a combination answer should not make incompatible claims about which actions occur. Temporal-order questions additionally require an ordering, rather than an unordered set. The dataset's `emotion` category was treated as manner-of-action classification; this is not a claim to infer a person's internal emotional state.

The historical data pipeline joined features and questions by recording identity, preserved missing-modality indicators, and mapped predicted action names back to each question's offered letters. Recording identifiers were join keys, not intended semantic features. Output validation checked the required answer grammar and official question order.

## Frozen visual representations

“Frozen” means that encoder weights were not updated during feature extraction. Downstream heads could still be trained. Different video encoders used different sampling contracts; the project did not use a single universal frame sampler.

| Representation | Implemented input and readout | Public release status |
| --- | --- | --- |
| OpenCLIP ViT-B/32, `laion2b_s34b_b79k` | Four individual frames per available view, square padding, frozen image embeddings, unit normalization | An adapted extractor is included in [research/frame_clip.py](../research/frame_clip.py) |
| R(2+1)D-18, Kinetics-400 weights | Historical general extractor: eight 16-frame windows on a 15 Hz decoded stream, motion crop, 112-pixel letterbox; 512 features per window | Historical pipeline, not included as a runnable extractor |
| InternVideo2-S14 | Historical initial extractor: eight frames across the video, motion crop, 224-pixel letterbox, ImageNet normalization; global and temporal features | Evaluated historical encoder; not the larger InternVideo2 variants and not bundled |
| V-JEPA 2 ViT-L | Centered native 64-frame experiment with a matched R(2+1)D control, detailed below | Completed research experiment; failed its improvement gates; not bundled |

### Correcting the frame-sheet input

The historical OpenCLIP input was a 1300×248 contact sheet containing four 320×240 tiles, four-pixel gaps and a four-pixel margin. Encoding that wide strip as one image lets a standard center crop discard much of its content. The corrected extractor separates the tiles, pads each to 320×320, and applies the encoder's transform to each frame independently.

It then computes a 512-dimensional image embedding, divides it by its L2 norm, and stores the four vectors per view. The historical cache also recorded view availability. The public adaptation preserves this preprocessing idea while changing file discovery and the output schema; it requires a user-supplied local checkpoint. It does not itself select video frames or train an answer predictor. [Optional extractor instructions](../research/README.md).

### What the V-JEPA 2 experiment actually did

The producing implementation and its preserved source snapshot were compared byte-for-byte for this account. The experiment covered all 809 HAU training recordings and both selected modalities: 1,618 views per encoder. Its checkpoint was [`facebook/vjepa2-vitl-fpc64-256`](https://huggingface.co/facebook/vjepa2-vitl-fpc64-256), revision `b3c1679b7c34d3255ef3547f27c7b226aefab26f`.

For a view with `N` native frames, selected indices were:

```text
start = max(0, floor((N - 64) / 2))
indices[k] = min(start + k, N - 1), for k = 0,...,63
```

FFprobe supplied each view's presentation timestamps and geometry. FFmpeg decoded the selected native indices without an FPS conversion, input seek, spatial resize or automatic rotation. Short videos repeated their last actual frame; repeated indices did not invent later timestamps. The selected interval covered one contiguous portion of the video, not its complete timeline. The preparation rejected unsupported rotation, malformed clocks and geometry beyond its fixed decoder bound.

A motion crop was estimated from 16 evenly spaced frames within those 64. The same source-coordinate crop fed both encoders. This did **not** make their final pixels identical:

- V-JEPA's processor resized the crop's shortest edge to 292, then center-cropped to 256×256 with bilinear antialiasing and ImageNet normalization.
- The matched R(2+1)D control letterboxed the crop to 112×112 with its Kinetics normalization and encoded four disjoint 16-frame chunks.

V-JEPA ran in evaluation mode using half precision and SDPA on Apple MPS. The unused predictor was removed before moving the encoder to the device; inference used `get_vision_features`. This was representation extraction, with no forecasting, planning or robot-control rollout.

The `[1, 8192, 1024]` patch output was reshaped into 32 temporal positions × 256 spatial tokens × 1024 channels. Spatial averaging produced **signed float32 `[32, 1024]`** features. The control produced `[4, 512]`. These representations were not passed through absolute-value, rectification or logarithmic compression.

Per view, readouts included temporal mean, population standard deviation, and eight phase-center vectors interpolated within the selected native interval. Duplicate timestamps were averaged before interpolation; endpoints were clamped. Phase was defined independently for each modality, not as a claim of exact cross-camera synchronization.

All raw feature shapes, timestamps, source hashes and aggregate readouts were audited. Successful extraction established a usable cache, not predictive superiority. The downstream results were:

| Correct answers | Standard | Stress |
| --- | ---: | ---: |
| Manner: corrected local reference / 809 | 427 | 430 |
| Manner: matched native64 R(2+1)D / 809 | 421 | 433 |
| Manner: native64 V-JEPA / 809 | 421 | 431 |
| Action: stronger local reference / 2,408 | 2,230 | 2,233 |
| Action: matched native64 R(2+1)D / 2,408 | 2,231 | 2,227 |
| Action: native64 V-JEPA / 2,408 | 2,230 | 2,225 |

Both V-JEPA studies failed their predeclared improvement criteria. In particular, the local manner reference was a separately trained model, not the inherited manner predictor in the submitted baseline. These counts cannot measure improvement against that inherited component.

## Learning from partial action labels

The local action pipeline combined visual features with sensor summaries. Masked kernel heads learned from known positive and negative clip/action pairs; unmentioned actions remained unknown. Subject-disjoint inner predictions trained fusion models, while outer held-out people were excluded from both stages. Later variants added complete-subset scoring for multi-action questions.

A useful supervision change came from auditing incorrect SINGLE alternatives. In the training population, these alternatives did not conflict with positives from sibling questions, allowing additional explicit negatives under this dataset's question contract. An incorrect combination was not treated as proof that all its constituent actions were absent. These are dataset-specific semantics, not rules to impose on arbitrary multiple-choice tasks.

The [joint action decoder](../src/cuhkx_portfolio/actions.py) enumerates compatible assignments and combines their scores. It can prevent one answer from selecting an action that another answer explicitly excludes. It does not create visual evidence or repair an incorrectly learned score. Its exhaustive search is suitable for small groups of questions; the public wrapper imposes a state limit. Margins are score gaps, not calibrated probabilities. Exact-tie behavior and other limitations are documented in the [code map](CODE_MAP.md).

## Targeted vision reasoning and routing

Later experiments supplied hosted vision models with chronological infrared/depth frames, questions and offered options. Validated responses were decoded into the original option space. Selected direct ORDER and HARn SINGLE routes entered submissions; many pairwise-order, split-timeline and manner experiments did not meet their original gates. Some later submissions were explicitly exploratory. Their leaderboard results must not be rewritten as prospective validation success. [Results](RESULTS.md).

The published [permutation utilities](../src/cuhkx_portfolio/permutation.py) illustrate a separate tested contract: relabel offered options, invert both returned order letters and evidence-anchor keys, and accept agreement only under a fixed rule; otherwise retain a supplied fallback. They make no model calls and are not evidence that agreement is accurate or that this experiment improved the best submission. Two responses from one model can share the same bias.

Routing operated on whole declared subsets with a retained baseline elsewhere. A valid merged CSV proves its assembly and protected rows, not the accuracy of its components. The best submission still retained inherited predictions, including the manner component. This repository does not claim to have recreated that component's underlying model.

## Validation and lessons from failures

The main local HAU studies used 18 training people, with three outer folds holding out six people each. A second three-fold partition tested sensitivity to the grouping. These partitions reused the same people and recordings across many experiments; they are development evidence, not six independent datasets or untouched confirmation.

We compared paired correct/incorrect changes, category totals and person-level changes, rather than relying only on aggregate accuracy. Later studies committed complete predictions before evaluation, replayed saved models in fresh processes, and kept failed attempts separate from technical repairs. These checks reduce implementation and accounting errors; they do not remove adaptive model-selection bias.

Source audits also found genuine defects: the wrong anatomical joint convention in an early pose feature map, duration averaging over a missing view, and unstable actor indices in multi-person pose output. Corrected representations require compatible models and renewed validation. A real preprocessing correction can lower accuracy, so neither a repaired bug nor a larger encoder was automatically promoted.
