from .types import Message


def default_formatter(_msg: Message, message: str, postfix: str) -> str:
    """Format a message.

    This is to be used by any method that does not have special way to handle
    messages (info, debug).

    Args:
        _msg: The message information.
        message: A formatted string that may include information from `_msg`.
        postfix: Anything that may need to be displayed after the message.

    Returns:
        A formatted string.
    """
    return f'{message}{postfix}'
