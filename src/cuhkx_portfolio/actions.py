"""Validated interface to the historical exhaustive action decoder.

An offered SINGLE choice is a positive observation, not an exhaustive inventory.
Unselected MULTI choices are explicit negatives under this task contract.
This semantic assumption must be checked before using the decoder on other tasks.
"""

import itertools
import math
from numbers import Real
import re


# These two normalization helpers are extracted from cuhkx.action_targets.
def normalize(value):
    return " ".join(re.sub(r"[^a-z0-9]+", " ", str(value).lower()).split())


def atoms(value):
    return tuple(normalize(v) for v in str(value).split(",") if v.strip())


def decode_actions(rows, probabilities, subset_scores=None, *, exclusive_single=False,
                   combination_penalty=0.0, categorical_logits=False,
                   max_assignments=100_000):
    """Return ``(answers, margins)`` for action questions grouped by recording.

    Each row needs ``clip``, unique ``qa_id``, ``category`` and options ``A``–``D``.
    Categories are single, combination, multi or sequence. Scores for the first
    three are probabilities keyed by question ID and offered option. Optional
    MULTI subset scores replace the independent-Bernoulli subset score.

    The search is exponential in questions per recording. A prospective state
    limit prevents accidental large searches. Margins are score gaps, not
    calibrated confidence; the historical sentinel 100 means no alternative
    consistent answer exists. Exact ties use lexical *labels*, not action text.
    """
    from ._joint_decode import joint_actions

    if type(max_assignments) is not int or max_assignments < 1:
        raise ValueError("max_assignments must be a positive integer")
    if type(exclusive_single) is not bool or type(categorical_logits) is not bool:
        raise ValueError("Decoder switches must be boolean")
    if not isinstance(combination_penalty, Real) or not math.isfinite(combination_penalty) or combination_penalty < 0:
        raise ValueError("combination_penalty must be finite and nonnegative")
    rows = list(rows)
    seen, groups, scored_ids, multi_ids = set(), {}, set(), set()
    for row in rows:
        if not isinstance(row.get("qa_id"), str) or not row["qa_id"] or row["qa_id"] in seen:
            raise ValueError("Question IDs must be unique nonempty strings")
        seen.add(row["qa_id"])
        if not isinstance(row.get("clip"), str) or not row["clip"]:
            raise ValueError("Each question must name its recording")
        category = row.get("category")
        if category not in {"single", "combination", "multi", "sequence"}:
            raise ValueError("Unsupported action question category")
        if any(not isinstance(row.get(letter), str) for letter in "ABCD"):
            raise ValueError("All four option fields must be strings; use empty strings for unavailable options")
        letters = [letter for letter in "ABCD" if row[letter].strip()]
        if not letters or (category == "sequence" and len(letters) != 4):
            raise ValueError("Missing offered options")
        if any(not atoms(row[letter]) or any(not atom for atom in atoms(row[letter])) for letter in letters):
            raise ValueError("Each offered option must contain a normalized action")
        if category == "sequence":
            continue
        qid = row["qa_id"]
        scored_ids.add(qid)
        scores = probabilities.get(qid, {})
        if set(scores) != set(letters):
            raise ValueError("Probability keys must exactly match offered options")
        if any(isinstance(p, bool) or not isinstance(p, Real) or not math.isfinite(p) or not 0 <= p <= 1 for p in scores.values()):
            raise ValueError("Probabilities must be finite numbers in [0, 1]")
        count = 2 ** len(letters) - 1 if category == "multi" else len(letters)
        groups[row["clip"]] = groups.get(row["clip"], 1) * count
        if groups[row["clip"]] > max_assignments:
            raise ValueError("Recording exceeds the exhaustive-search state limit")
        if category == "multi":
            multi_ids.add(qid)
            if subset_scores is not None and qid in subset_scores:
                expected = {"".join(c) for n in range(1, len(letters) + 1) for c in itertools.combinations(letters, n)}
                supplied = subset_scores[qid]
                if set(supplied) != expected or any(isinstance(v, bool) or not isinstance(v, Real) or not math.isfinite(v) for v in supplied.values()):
                    raise ValueError("Subset scores must cover every nonempty subset with finite values")
    if set(probabilities) != scored_ids:
        raise ValueError("Probability IDs must match the scored questions")
    if subset_scores is not None and not set(subset_scores) <= multi_ids:
        raise ValueError("Subset scores belong only to MULTI questions")
    return joint_actions(rows, probabilities, subset_scores,
                         exclusive_single=exclusive_single,
                         combination_penalty=combination_penalty,
                         categorical_logits=categorical_logits)
