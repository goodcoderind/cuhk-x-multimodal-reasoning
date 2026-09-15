"""Portable adaptation of the project's fixed option-permutation contract.

No model is called here. Agreement is not proof of correctness or independent
evidence: two prompts can share the same model bias.
"""

from collections.abc import Mapping

LETTERS = "ABCD"


def _mapping(public_to_base):
    if not isinstance(public_to_base, Mapping) or set(public_to_base) != set(LETTERS) or set(public_to_base.values()) != set(LETTERS):
        raise ValueError("Mapping must be a bijection from A-D to A-D")


def _order(order):
    if not isinstance(order, str) or len(order) != 4 or set(order) != set(LETTERS):
        raise ValueError("An order must contain A-D exactly once")


def remap_options(base_options, public_to_base):
    """Relabel offered text: new public A receives base_options[mapping[A]]."""
    _mapping(public_to_base)
    if set(base_options) != set(LETTERS):
        raise ValueError("Exactly four base options are required")
    return {letter: base_options[public_to_base[letter]] for letter in LETTERS}


def remap_order_response(response, public_to_base, *, attachment_count):
    """Map order letters AND anchor keys back; attachment indices stay fixed.

    Anchor zero denotes unavailable evidence. Unknown fields, boolean anchors,
    duplicate letters and out-of-range indices are rejected. HIGH uncertainty
    is preserved but is not an additional confidence filter.
    """
    _mapping(public_to_base)
    if type(attachment_count) is not int or attachment_count < 1:
        raise ValueError("attachment_count must be a positive integer")
    if not isinstance(response, Mapping) or set(response) != {"order", "anchors", "uncertainty"}:
        raise ValueError("Response fields differ from the contract")
    _order(response["order"])
    anchors = response["anchors"]
    if not isinstance(anchors, Mapping) or set(anchors) != set(LETTERS):
        raise ValueError("Each offered label needs an anchor")
    if any(type(value) is not int or not 0 <= value <= attachment_count for value in anchors.values()):
        raise ValueError("Anchors must be integer indices in [0, attachment_count]")
    if response["uncertainty"] not in ("low", "medium", "high"):
        raise ValueError("Unknown uncertainty value")
    return {
        "order": "".join(public_to_base[letter] for letter in response["order"]),
        "anchors": {public_to_base[letter]: anchors[letter] for letter in LETTERS},
        "uncertainty": response["uncertainty"],
    }


def agreement_or_fallback(fallback, first_response, second_response, *,
                          first_mapping, second_mapping, attachment_count):
    """Return a mapped agreement only when both complete responses have evidence.

    Malformed responses raise; valid responses with absent anchors or disagreeing
    orders retain the supplied fallback. The caller owns transport validation.
    The rule cannot choose whichever individual response later scores best.
    """
    _order(fallback)
    first = remap_order_response(first_response, first_mapping, attachment_count=attachment_count)
    second = remap_order_response(second_response, second_mapping, attachment_count=attachment_count)
    usable = all(first["anchors"].values()) and all(second["anchors"].values())
    return first["order"] if usable and first["order"] == second["order"] else fallback
