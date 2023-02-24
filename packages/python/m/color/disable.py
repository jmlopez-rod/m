import os


def color_disabled() -> bool:
    """Check for environment variable NO_COLOR.

    Utilities that format strings with color should call this function
    to determine if the user wants color in the final output.

    Returns:
        True if it exists and its set to true or 1.
    """
    return os.environ.get('NO_COLOR', 'false') in {'true', '1', 'True'}
