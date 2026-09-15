import copy
import itertools
import unittest

from cuhkx_portfolio import agreement_or_fallback, remap_options, remap_order_response

IDENTITY = dict(zip("ABCD", "ABCD"))
REVERSE = dict(zip("ABCD", "DCBA"))


class PermutationContractTest(unittest.TestCase):
    def test_every_mapping_and_order_round_trips_with_anchor_identity(self):
        options = dict(zip("ABCD", ["walk", "sit", "drink", "stand"]))
        for labels in itertools.permutations("ABCD"):
            mapping = dict(zip("ABCD", labels))
            inverse = {base: public for public, base in mapping.items()}
            offered = remap_options(options, mapping)
            for public, base in mapping.items():
                self.assertEqual(offered[public], options[base])
            for order in itertools.permutations("ABCD"):
                response = dict(order="".join(order), anchors=dict(zip("ABCD", [2, 7, 12, 19])), uncertainty="high")
                mapped = remap_order_response(response, mapping, attachment_count=20)
                self.assertEqual(remap_order_response(mapped, inverse, attachment_count=20), response)
                for public, base in mapping.items():
                    self.assertEqual(mapped["anchors"][base], response["anchors"][public])

    def test_agreement_can_override_and_high_uncertainty_is_not_extra_filter(self):
        first = dict(order="ABCD", anchors=dict(zip("ABCD", [1, 2, 3, 4])), uncertainty="high")
        second = dict(order="DCBA", anchors=dict(zip("ABCD", [4, 3, 2, 1])), uncertainty="high")
        self.assertEqual(agreement_or_fallback("BACD", first, second, first_mapping=IDENTITY,
                         second_mapping=REVERSE, attachment_count=4), "ABCD")

    def test_disagreement_or_absent_evidence_keeps_the_fixed_fallback(self):
        first = dict(order="ABCD", anchors=dict.fromkeys("ABCD", 1), uncertainty="low")
        second = dict(order="ABCD", anchors=dict.fromkeys("ABCD", 1), uncertainty="low")
        self.assertEqual(agreement_or_fallback("BACD", first, second, first_mapping=IDENTITY,
                         second_mapping=REVERSE, attachment_count=4), "BACD")
        second["order"] = "DCBA"
        second["anchors"]["A"] = 0
        self.assertEqual(agreement_or_fallback("BACD", first, second, first_mapping=IDENTITY,
                         second_mapping=REVERSE, attachment_count=4), "BACD")

    def test_malformed_evidence_is_an_error_not_silent_fallback(self):
        valid = dict(order="ABCD", anchors=dict.fromkeys("ABCD", 1), uncertainty="low")
        for invalid in (True, -1, 5, float("nan")):
            bad = copy.deepcopy(valid)
            bad["anchors"]["A"] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                remap_order_response(bad, IDENTITY, attachment_count=4)
        with self.assertRaises(ValueError):
            remap_order_response({**valid, "order": "AABC"}, IDENTITY, attachment_count=4)
        with self.assertRaises(ValueError):
            remap_order_response(valid, dict.fromkeys("ABCD", "A"), attachment_count=4)
        with self.assertRaises(ValueError):
            remap_order_response({**valid, "hidden": "field"}, IDENTITY, attachment_count=4)


if __name__ == "__main__":
    unittest.main()
