from m.core.io import env


class Color:
    """A class for terminal color codes."""

    bold = '\033[1m'
    blue = '\033[94m'
    aqua = '\033[96m'
    white = '\033[97m'
    green = '\033[92m'
    yellow = '\033[93m'
    gray = '\033[90m'
    red = '\033[91m'
    bold_white = bold + white
    bold_blue = bold + blue
    bold_aqua = bold + aqua
    bold_green = bold + green
    bold_yellow = bold + yellow
    bold_gray = bold + gray
    bold_red = bold + red
    end = '\033[0m'


color_dict = {
    color_name: color_value
    for color_name, color_value in Color.__dict__.items()
    if color_name[0] != '_'
}
no_color_dict = {color_name: '' for color_name in color_dict}


def color(*args: str, auto_end=True) -> str:
    r"""Color a message.

    Formats the message by replacing the colors in the Colors class.
    For instance::

        color('{blue}Hello there{end}\n{yellow}WARNING{end}')

    We can turn off colors by declaring the environment variable
    NO_COLOR.

    Args:
        args: Strings to color
        auto_end: Adds a string to end coloring

    Returns:
        A formatted message.
    """
    no_color = env('NO_COLOR', 'false') == 'true'
    color_map = no_color_dict if no_color else color_dict
    end = '' if no_color or not auto_end else Color.end
    msg_list = [msg.format(**color_map) for msg in args]
    return ''.join(msg_list) + end
