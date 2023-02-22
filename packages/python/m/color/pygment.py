
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexer import Lexer
from pygments.lexers.data import YamlLexer
from pygments.lexers.web import JsonLexer
from pygments.styles import get_style_by_name

from .disable import color_disabled

style = get_style_by_name('github-dark')
terminal_formatter = Terminal256Formatter(style=style)


def _highlight(text: str, lexer: Lexer) -> str:
    if color_disabled():
        return text
    try:
        return highlight(text, lexer=lexer, formatter=terminal_formatter)
    except Exception:
        return text


def highlight_json(text: str) -> str:
    """Highlight a json string.

    Args:
        text: The json string to highlight.

    Returns:
        A colorized json string.
    """
    return _highlight(text, JsonLexer())


def highlight_yaml(text: str) -> str:
    """Highlight a yaml string.

    Args:
        text: The yaml string to highlight.

    Returns:
        A colorized yaml string.
    """
    return _highlight(text, YamlLexer())
