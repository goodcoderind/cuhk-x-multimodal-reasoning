import itertools
import math
import unittest

from cuhkx_portfolio import decode_actions
from cuhkx_portfolio._joint_decode import joint_actions


def row(qid, category, options, clip="synthetic"):
    return dict(qa_id=qid, category=category, clip=clip, **dict(zip("ABCD", options)))


class ActionConstraintsTest(unittest.TestCase):
    def test_single_is_positive_not_an_exhaustive_inventory(self):
        rows = [row("s", "single", ["walk", "jump", "dance", "clap"]),
                row("m", "multi", ["walk", "drink", "jump", "wave"])]
        probabilities = {"s": dict(A=.999, B=.001, C=.001, D=.001),
                         "m": dict(A=.1, B=.9, C=.01, D=.01)}
        answers, margins = decode_actions(rows, probabilities)
        self.assertEqual(answers, {"s": "A", "m": "AB"})
        self.assertTrue(all(gap >= 0 for gap in margins.values()))

    def test_wrong_combination_does_not_negate_each_of_its_atoms(self):
        rows = [row("c", "combination", ["walk, sit", "jump, run", "sit, wave", "run, wave"]),
                row("m", "multi", ["walk", "sit", "jump", "wave"])]
        probabilities = {"c": dict(A=.999, B=.001, C=.001, D=.001),
                         "m": dict(A=.8, B=.8, C=.9, D=.1)}
        self.assertEqual(decode_actions(rows, probabilities)[0], {"c": "A", "m": "ABC"})

    def test_every_sequence_option_implies_presence_regardless_of_order(self):
        sequence = ["walk", "drink", "sit", "stand"]
        for options in itertools.permutations(sequence):
            rows = [row("q", "sequence", options), row("m", "multi", ["walk", "drink", "jump", "wave"])]
            answers, _ = decode_actions(rows, {"m": dict(A=.01, B=.01, C=.01, D=.01)})
            self.assertEqual(answers, {"m": "AB"})

    def test_optional_single_exclusion_only_affects_offered_distractors(self):
        rows = [row("s", "single", ["walk", "jump", "dance", "clap"]),
                row("m", "multi", ["walk", "sit", "jump", "wave"])]
        probabilities = {"s": dict(A=.999, B=.001, C=.001, D=.001),
                         "m": dict(A=.8, B=.8, C=.8, D=.1)}
        self.assertEqual(decode_actions(rows, probabilities)[0]["m"], "ABC")
        self.assertEqual(decode_actions(rows, probabilities, exclusive_single=True)[0]["m"], "AB")

    def test_inconsistent_contract_raises_instead_of_choosing_silently(self):
        rows = [row("s", "single", ["walk", "walk", "walk", "walk"])]
        with self.assertRaisesRegex(ValueError, "No consistent"):
            decode_actions(rows, {"s": dict.fromkeys("ABCD", .5)}, exclusive_single=True)

    def test_public_boundary_rejects_nonfinite_probabilities_and_duplicate_ids(self):
        rows = [row("s", "single", ["walk", "sit", "jump", "wave"])]
        for value in (math.nan, math.inf, -1, 1.1, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                decode_actions(rows, {"s": dict(A=value, B=.2, C=.3, D=.4)})
        with self.assertRaises(ValueError):
            decode_actions(rows * 2, {"s": dict.fromkeys("ABCD", .5)})

    def test_exponential_search_has_explicit_prospective_limit(self):
        rows = [row(str(i), "multi", ["walk", "sit", "jump", "wave"]) for i in range(5)]
        with self.assertRaisesRegex(ValueError, "state limit"):
            decode_actions(rows, {str(i): dict.fromkeys("ABCD", .5) for i in range(5)}, max_assignments=100)

    def test_subset_score_contract_and_historical_scoring_parity(self):
        rows = [row("m", "multi", ["walk", "sit", "jump", "wave"])]
        probabilities = {"m": dict.fromkeys("ABCD", .5)}
        subsets = {"".join(c): -3.0 for size in range(1, 5) for c in itertools.combinations("ABCD", size)}
        subsets["CD"] = 4.0
        actual = decode_actions(rows, probabilities, {"m": subsets})
        self.assertEqual(actual[0], {"m": "CD"})
        self.assertEqual(actual, joint_actions(rows, probabilities, {"m": subsets}))
        with self.assertRaises(ValueError):
            decode_actions(rows, probabilities, {"m": {"CD": 4.0}})

    def test_exact_historical_ties_are_label_based(self):
        rows = [row("s", "single", ["zebra pose", "alpha pose", "walk", "sit"])]
        self.assertEqual(decode_actions(rows, {"s": dict.fromkeys("ABCD", .5)})[0], {"s": "A"})


if __name__ == "__main__":
    unittest.main()
