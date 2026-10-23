"""Classification handling: what the system accepts, and how labels propagate."""

from __future__ import annotations

from collections.abc import Iterable

from tra_core.schemas import Classification

# The design is accredited for OFFICIAL: Sensitive. PROTECTED is a future state.
MAX_ACCEPTED = Classification.OFFICIAL_SENSITIVE

# A TRA lists a system's weaknesses, so it is at least OFFICIAL: Sensitive.
TRA_FLOOR = Classification.OFFICIAL_SENSITIVE


class ClassificationError(Exception):
    pass


def highest(labels: Iterable[Classification]) -> Classification:
    labels = list(labels)
    if not labels:
        raise ClassificationError("no labels to combine")
    return max(labels, key=lambda c: c.rank)


def check_accepted(label: Classification) -> None:
    if label.rank > MAX_ACCEPTED.rank:
        raise ClassificationError(
            f"{label.label} material is not accepted: this deployment is limited to {MAX_ACCEPTED.label}"
        )


def derived_label(inputs: Iterable[Classification]) -> Classification:
    """Label for anything derived from the inputs: their highest, never below the TRA floor."""
    return highest([*inputs, TRA_FLOOR])


def can_read(clearance: Classification, label: Classification) -> bool:
    return clearance.rank >= label.rank
