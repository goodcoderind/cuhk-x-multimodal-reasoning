import unittest

from cuhkx_portfolio import grouped_holdout


class GroupedHoldoutTest(unittest.TestCase):
    def setUp(self):
        self.rows = [dict(qa_id=f"q{i}", person=person, recording=recording)
                     for i, (person, recording) in enumerate([
                         (1, "r1"), (2, "r2"), (1, "r1"), (3, "r3"),
                         (2, "r2"), (1, "r4"), (3, "r5"),
                     ])]

    def test_siblings_stay_together_and_all_rows_are_retained_in_order(self):
        split = grouped_holdout(self.rows, {2})
        self.assertEqual(split.train_indices, (0, 2, 3, 5, 6))
        self.assertEqual(split.validation_indices, (1, 4))
        self.assertFalse(split.train_people & split.validation_people)
        self.assertEqual(sorted(split.train_indices + split.validation_indices), list(range(7)))
        train_recordings = {self.rows[i]["recording"] for i in split.train_indices}
        held_recordings = {self.rows[i]["recording"] for i in split.validation_indices}
        self.assertFalse(train_recordings & held_recordings)

    def test_row_permutation_does_not_change_membership(self):
        split = grouped_holdout(self.rows, {1, 3})
        reversed_rows = list(reversed(self.rows))
        reversed_split = grouped_holdout(reversed_rows, {1, 3})
        self.assertEqual({self.rows[i]["qa_id"] for i in split.validation_indices},
                         {reversed_rows[i]["qa_id"] for i in reversed_split.validation_indices})

    def test_recording_identity_cannot_cross_people(self):
        bad = [*self.rows, dict(qa_id="new", person=2, recording="r1")]
        with self.assertRaisesRegex(ValueError, "multiple people"):
            grouped_holdout(bad, {2})

    def test_duplicate_missing_and_empty_split_fail_closed(self):
        bad_cases = [(self.rows + [self.rows[0]], {2}), (self.rows, {99}),
                     (self.rows, {1, 2, 3}), (self.rows, set()),
                     ([dict(qa_id="x", person=None, recording="r")], {1})]
        for rows, held in bad_cases:
            with self.subTest(held=held), self.assertRaises(ValueError):
                grouped_holdout(rows, held)


if __name__ == "__main__":
    unittest.main()
