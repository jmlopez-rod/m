import json
import textwrap


def indent_payload(
    indent: int,
    payload: dict,
    prepend_new_line: bool = True,
) -> str:
    """Stringify a dictionary as JSON and indent it.

    Args:
        indent: The number of spaces to indent.
        payload: The data to stringify and indent.
        prepend_new_line: Prepend a new line to the payload if `True`.

    Returns:
        An indented payload.
    """
    json_dict = json.dumps(payload, indent=2)
    indented_payload = textwrap.indent(json_dict, ' ' * indent)
    return f'\n{indented_payload}' if prepend_new_line else indented_payload
