from enum import Enum


class PullRequestReviewState(str, Enum):  # noqa: WPS600
    """Possible choices for a pull request review state."""

    # A review allowing the pull request to merge.
    approved = 'APPROVED'

    # A review blocking the pull request from merging.
    changes_requested = 'CHANGES_REQUESTED'

    # An informational review.
    commented = 'COMMENTED'

    # A review that has been dismissed.
    dismissed = 'DISMISSED'

    # A review that has not yet been submitted.
    pending = 'PENDING'


class MergeableState(str, Enum):  # noqa: WPS600
    """Whether or not a PullRequest can be merged."""

    # The pull request cannot be merged due to merge conflicts.
    conflicting = 'CONFLICTING'

    # The pull request can be merged.
    mergeable = 'MERGEABLE'

    # The mergeability of the pull request is still being calculated.
    unknown = 'UNKNOWN'
