from m.core import Good, Issue, OneOf, issue

YES_NO = ('yes', 'no')


def is_yes(user_response: str) -> bool:
    """Assert the user response is "yes".

    Args:
        user_response: user's response

    Returns:
        True if the string is "yes".
    """
    return user_response == 'yes'


def assert_branch(branch: str, step: str) -> OneOf[Issue, tuple[str, str]]:
    """Assert that a release step is done in the proper branch.

    This can only happen in `release/x.y.z` or `hotfix/x.y.z`.

    Args:
        branch: branch name to verify.
        step: the release step name.

    Returns:
        An Issue if the current branch is not a release/hotfix else the
        release type and version to release/hotfix.
    """
    valid_prefix = ('release/', 'hotfix/')
    if branch.startswith(valid_prefix):
        parts = branch.split('/')
        return Good((parts[0], parts[1]))
    return issue(
        f'{step}_release can only be done from a release/hotfix branch',
        context={
            'current_branch': branch,
            'expected': 'release/x.y.z or hotfix/x.y.z',
        },
    )
