"""New synthetic demonstration: no dataset, weights, network, credentials or fits.

From the repository root: PYTHONPATH=src python -m cuhkx_portfolio.demo
"""

import json
from cuhkx_portfolio import agreement_or_fallback, decode_actions, grouped_holdout, remap_order_response


def main():
    rows = [
        dict(clip="synthetic-recording", qa_id="single", category="single", A="walk", B="jump", C="dance", D="clap"),
        dict(clip="synthetic-recording", qa_id="multi", category="multi", A="walk", B="drink", C="jump", D="wave"),
    ]
    scores = {"single": dict(A=.999, B=.001, C=.001, D=.001),
              "multi": dict(A=.1, B=.9, C=.01, D=.01)}
    answers, margins = decode_actions(rows, scores)
    population = [dict(qa_id=f"q{person}_{question}", person=person, recording=f"r{person}")
                  for person in (1, 2, 3) for question in ("single", "multi")]
    split = grouped_holdout(population, {3})
    identity, reverse = dict(zip("ABCD", "ABCD")), dict(zip("ABCD", "DCBA"))
    original = dict(order="ABCD", anchors=dict(zip("ABCD", [1, 2, 3, 4])), uncertainty="high")
    rotated = dict(order="DCBA", anchors=dict(zip("ABCD", [4, 3, 2, 1])), uncertainty="high")
    consensus = agreement_or_fallback("BACD", original, rotated, first_mapping=identity,
                                      second_mapping=reverse, attachment_count=4)
    report = {
        "kind": "synthetic_engineering_demo_not_benchmark_results",
        "models_called": 0,
        "fits": 0,
        "constraints": {"independent_multi_threshold_answer": "B", "joint_answers": answers,
                        "score_margins_not_confidence": margins,
                        "explanation": "The selected SINGLE supports walk; MULTI retains walk and drink."},
        "group_split": {"train_question_ids": [population[i]["qa_id"] for i in split.train_indices],
                        "held_question_ids": [population[i]["qa_id"] for i in split.validation_indices]},
        "option_mapping": {"reversed_response_in_original_labels": remap_order_response(rotated, reverse, attachment_count=4),
                           "fixed_fallback": "BACD", "agreement": consensus},
    }
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
