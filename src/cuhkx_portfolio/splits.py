"""New stdlib adapter for the historical held-person validation strategy."""

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class Holdout:
    """Row indices preserve input order and partition the complete input."""

    train_indices: tuple[int, ...]
    validation_indices: tuple[int, ...]
    train_people: frozenset
    validation_people: frozenset


def _identifier(value):
    return (isinstance(value, str) and bool(value.strip())) or type(value) is int


def grouped_holdout(rows: Sequence[Mapping], validation_people) -> Holdout:
    """Split question rows by explicit person IDs, never by individual question.

    Rows contain ``qa_id``, ``person`` and globally unique ``recording`` IDs.
    Sibling questions from a recording must name the same person. Explicit IDs
    avoid a dependency on dataset-specific path parsing. Missing held people,
    duplicate question IDs and inconsistent recording ownership fail closed.

    This prevents person/recording overlap only. It does not establish routine,
    session or distribution independence; callers must define those separately.
    """
    held = frozenset(validation_people)
    if not held or any(not _identifier(person) for person in held):
        raise ValueError("Supply nonempty valid held-person IDs")
    seen, owners, people, train, validation = set(), {}, set(), [], []
    for index, row in enumerate(rows):
        qid, person, recording = (row.get(key) for key in ("qa_id", "person", "recording"))
        if not all(_identifier(value) for value in (qid, person, recording)):
            raise ValueError("Question, person and recording IDs are required")
        if qid in seen:
            raise ValueError("Duplicate question ID")
        seen.add(qid)
        if recording in owners and owners[recording] != person:
            raise ValueError("One recording cannot belong to multiple people")
        owners[recording] = person
        people.add(person)
        (validation if person in held else train).append(index)
    if not held <= people:
        raise ValueError("A requested held person is missing from the population")
    if not train or not validation:
        raise ValueError("Both partitions must be nonempty")
    return Holdout(tuple(train), tuple(validation), frozenset(people - held), held)
