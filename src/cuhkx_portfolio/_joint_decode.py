"""Enforce positive/negative action consistency across questions for one clip.

Single/combination answers specify positives, not exhaustive action inventories.
Multi selections identify explicit negatives; optional single exclusion does
so for offered distractors too. Every sequence option must occur regardless of
its order. These constraints use no answer labels.
"""
import itertools
import math

from .actions import atoms


def joint_actions(rows, probabilities, subset_scores=None, *, exclusive_single=False,
                  combination_penalty=0., categorical_logits=False):
    """Decode with optional single-question distractor exclusion.

    The selected single action is not an exhaustive action inventory. Only its
    explicitly offered incorrect alternatives become negative when enabled.
    An optional soft penalty discourages a wrong combination whose atoms are
    all positive. It never marks all wrong combination atoms individually absent.
    categorical_logits uses conditional-Bernoulli log-odds instead of log(p)
    for single/combination scores; defaults off for existing checkpoints.
    """
    if not math.isfinite(combination_penalty) or combination_penalty < 0:
        raise ValueError("combination_penalty must be finite and nonnegative")
    groups = {}
    for r in rows:
        groups.setdefault(r["clip"], []).append(r)
    predictions, margins = {}, {}
    for group in groups.values():
        eligible = [r for r in group if r["category"] in {"single", "combination", "multi"}]
        if not eligible:
            continue
        sequence_positives = {a for r in group if r["category"] == "sequence" for l in "ABCD" for a in atoms(r[l])}
        candidates = []
        for r in eligible:
            letters = [l for l in "ABCD" if str(r[l]).strip()]
            opts = probabilities[r["qa_id"]]
            answers = ["".join(c) for n in range(1, len(letters)+1) for c in itertools.combinations(letters, n)] if r["category"] == "multi" else letters
            scored = []
            for answer in answers:
                positive = {a for l in answer for a in atoms(r[l])}
                has_negatives = r["category"] == "multi" or (exclusive_single and r["category"] == "single")
                negative = {a for l in letters if l not in answer for a in atoms(r[l])} if has_negatives else set()
                p = {l: min(max(opts[l], .000001), .999999) for l in letters}
                score = sum(math.log(p[l] if l in answer else 1 - p[l]) for l in letters) if r["category"] == "multi" else math.log(p[answer])
                if categorical_logits and r["category"] != "multi":
                    score -= math.log1p(-p[answer])
                if r["category"] == "multi" and subset_scores is not None and r["qa_id"] in subset_scores:
                    score = subset_scores[r["qa_id"]][answer]
                scored.append((answer, positive, negative, score))
            candidates.append(scored)
        possible = []
        for selection in itertools.product(*candidates):
            positives = sequence_positives | set.union(*(v[1] for v in selection))
            negatives = set.union(*(v[2] for v in selection))
            if positives & negatives:
                continue
            violations = 0
            if combination_penalty:
                for r, v in zip(eligible, selection):
                    if r["category"] == "combination":
                        violations += sum(bool(atoms(r[l])) and set(atoms(r[l])) <= positives
                                          for l in "ABCD" if l != v[0])
            score = sum(v[3] for v in selection) - combination_penalty * violations
            possible.append((score, tuple(v[0] for v in selection)))
        if not possible:
            raise ValueError("No consistent action assignment exists")
        possible.sort(key=lambda v: (-v[0], v[1]))
        best_score, best = possible[0]
        for i, r in enumerate(eligible):
            alternatives = [s for s, answers in possible if answers[i] != best[i]]
            predictions[r["qa_id"]] = best[i]
            margins[r["qa_id"]] = best_score - max(alternatives) if alternatives else 100.
    return predictions, margins
