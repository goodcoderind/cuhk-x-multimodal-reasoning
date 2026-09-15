# Attribution and release boundary

## Benchmark and public baseline

The task, data, question construction and evaluation belong to the organizers and contributors of the [CUHK-X Competition, Large Model Track](https://www.kaggle.com/competitions/cuhk-x-competition-large-model-track). This repository is an independent portfolio presentation, not an official benchmark release or an endorsement by the organizers.

**Fususu, publishing as `phuongncn`, must be credited for the public 0.77777 starting artifact:** [“LB 0.77777 Exact Submission Research Handoff”](https://www.kaggle.com/code/phuongncn/lb-0-77777-exact-submission-research-handoff). The archived source was notebook version 2. It supplied a published prediction vector, not the full specialist training/inference pipeline and checkpoints needed to regenerate that vector.

This project built local models and task-specific overlays around that inherited baseline. It does not claim authorship of the baseline predictions or their underlying models. In particular, the best submission retained all 144 inherited MANNER answers. Later local MANNER validation numbers describe separately implemented reference models; they must not be presented as the validation accuracy of the inherited predictor.

The baseline notebook and prediction vector are **not redistributed** in this repository. Consult their original source for applicable terms. Availability of an artifact online is not treated as blanket permission to redistribute its code, predictions, data or model weights.

## Tools and models used in the broader research

The historical work used the Python scientific ecosystem, including NumPy, pandas, SciPy, scikit-learn and PyTorch; video preparation used FFmpeg and OpenCV. Some experiments used pretrained encoders, including CLIP, and hosted OpenAI vision-language models. Their implementations, pretrained weights and services remain the work of their respective authors and providers.

These acknowledgments describe the broader research environment, not a claim that every dependency or model is included in the curated package. Model access and upstream licenses are separate from the license on original material released here. The published package's actual dependencies are listed in its project configuration.

## What this portfolio contains

The public release contains curated project-written utilities, generated examples, tests, aggregate results and methodological notes. It excludes benchmark media and labels, per-question prediction vectors, raw hosted-model responses, private checkpoints and caches, account/session records, and private experiment paths.

AI coding assistants supported implementation, testing, experiment operations and documentation. Their assistance is not independent empirical evidence; numerical claims here are grounded in recorded experiment and submission results. Responsibility for the selected methodology, reported limitations and published repository remains with the project author.

The repository's license applies to original material included in this release. It does not relicense third-party artifacts or confer access to the benchmark or hosted models. The exact upstream generator of the inherited MANNER baseline remains an explicit reproducibility limitation, not a missing implementation being claimed as complete.
