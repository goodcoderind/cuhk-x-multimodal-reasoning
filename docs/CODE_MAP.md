# What this repository implements

This is a small public engineering portfolio extracted from a larger private
experiment workspace. It contains real historical decoding logic, portable
adaptations of evaluation contracts, and a newly written synthetic example.
It does **not** reproduce the full competition pipeline or the reported 0.88304
submission. No training data, private images, saved model responses, submission
answers, model weights or credentials are included.

## Code and provenance

| Public component | Historical source | What is preserved or changed |
| --- | --- | --- |
| [`_joint_decode.py`](../src/cuhkx_portfolio/_joint_decode.py) | `src/cuhkx/joint_decode.py` | Historical exhaustive search, consistency constraints, probability clipping, optional penalties, score margins and tie behavior are preserved verbatim. The only source change is the import of `atoms` from the portable module. This is the actual implemented decoder, not newly invented pseudocode. |
| [`actions.py`](../src/cuhkx_portfolio/actions.py) | `normalize` and `atoms` in `src/cuhkx/action_targets.py` | The two normalization helpers are unchanged. `decode_actions` is a **new portfolio boundary** that checks IDs, categories, offered score coverage, finite values and an explicit search-size limit before invoking the historical decoder. The original NumPy target-building functions are not included. |
| [`splits.py`](../src/cuhkx_portfolio/splits.py) | Held-person strategy in `src/cuhkx/data.py::split_by_users` | **New stdlib implementation**, not a verbatim extraction. It uses explicit person/recording IDs and returns row indices instead of parsing dataset paths and returning pandas frames. Added checks reject inconsistent recording ownership, duplicate question IDs, missing requested people and empty partitions. |
| [`permutation.py`](../src/cuhkx_portfolio/permutation.py) | `mapped`, `validate`, `consensus` in `artifacts/astra_final_order_consensus_20260915/audit.py` | **Portable adaptation** of the implemented contract: map order letters and anchor keys together, keep attachment indices unchanged, require complete supported agreement or retain a fixed fallback. The public functions accept explicit permutations and validate arguments. They do not include transport, real requests, predictions, grading or submission machinery. Inclusion does not claim this later consensus experiment improved the competition score. |
| [`demo.py`](../src/cuhkx_portfolio/demo.py), [`offline_demo.py`](../examples/offline_demo.py) | None | **New synthetic demonstration** of the public APIs. Option scores, actions, people, recordings and evidence indices are invented fixtures. Nothing is fitted or inferred from private data. |
| [`tests/`](../tests/) | Historical regression ideas plus new fixtures | **New unittest suite**. Covers partial-action semantics, inconsistent constraints, malformed probabilities, state limits, group leakage, 24×24 order/permutation round trips, anchor identity and deterministic fallback. Historical scoring parity is checked against the included search implementation. Tests do not establish model accuracy. |
| [`research/frame_clip.py`](../research/frame_clip.py) | `scripts/encode_frame_clip.py` | **New manifest-based adaptation by the repository author**, not a historical cache replay. Retains the useful frame-level CLIP extraction idea while replacing workspace-specific CSV/contact-sheet discovery with explicit local inputs and checkpoint configuration. Its optional dependencies and data prerequisites are separate from the dependency-free package. It does not include OpenCLIP implementation code or checkpoint weights. |

Source snapshots used for the extraction and adaptations:

| Historical file | SHA-256 |
| --- | --- |
| `src/cuhkx/joint_decode.py` | `d7781a3a335024f14b0b41854df48f486bc3bcc56d037ca20773e5a8aac3c6fd` |
| `src/cuhkx/action_targets.py` | `853ac4a59828f557263fa4674ececa8824d0301991a5f55a24115b8c3a371bcb` |
| `src/cuhkx/data.py` | `834320dc3a994365bfa6d8b741597102ac50e73b2d4e6689f07c009fe9adf4cb` |
| `artifacts/astra_final_order_consensus_20260915/audit.py` | `0adc1573d037b4325a04f0608cc6422ad371eccb5283f89b146bf4c5f70cebdc` |

These hashes identify the local source snapshots; they are not public data
downloads or evidence that the benchmark is independently reproducible.
The included core files were checked for embedded data, credentials and apparent
third-party source headers. No vendor model implementation was copied into them.
Third-party libraries/models used by optional research scripts retain their own
licenses; see [attribution](ATTRIBUTION.md).

## Contracts worth inspecting

**Action consistency.** A SINGLE answer says one action occurred; it does not say
all other actions were absent. A selected COMBINATION supplies its constituent
positives, while a wrong conjunction does not individually negate every member.
Under this task's MULTI contract, offered but unselected options are explicit
negatives. Every SEQUENCE option contributes a positive regardless of its order.
The decoder rejects assignments that require an action to be both present and
absent. These are task-specific assumptions, not universal language semantics.

**Search and uncertainty.** The decoder enumerates possible answer combinations
per recording, so runtime grows exponentially. The public wrapper caps the
prospective number of assignments. Probability clipping and lexical label ties
are historical behavior. A returned margin is a difference in objective scores,
not a calibrated probability; `100` is the historical sentinel for no consistent
alternative. Exact score ties can change semantic choice under relabeling, and
the tests/documentation do not promise otherwise.

**Validation groups.** All questions from a held person stay outside the training
partition. Recording ownership checks catch sibling leakage caused by inconsistent
metadata. This alone does not establish held-routine, session or distribution
independence, and the API does not claim to implement those other split designs.

**Option permutations.** If new option A names old action D, both an A in the
returned order and the anchor stored under A must map to D. The image index itself
must not change. Syntactically valid responses with anchor zero or disagreement
retain the supplied fallback; malformed responses raise. Uncertainty is retained
as metadata, not used as a new filter. Agreement is not proof of correctness.

## Run without data or installation

Python 3.10 or later is sufficient for the public package and generated tests:

```bash
PYTHONPATH=src python -m cuhkx_portfolio.demo
PYTHONPATH=src python -m unittest discover -s tests -v
```

Alternatively, `python examples/offline_demo.py` runs the same example directly
from a checkout. The demo prints JSON and performs no network, model, training,
credential or dataset operations. Installing the package with a build frontend
uses setuptools; that packaging step is optional for these commands.
