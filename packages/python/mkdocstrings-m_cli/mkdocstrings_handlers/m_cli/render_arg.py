from markupsafe import Markup
from mkdocstrings.handlers.base import BaseHandler

from .field_parser import ArgParseInfo


def render_cli_arguments(  # noqa: WPS211
    plugin_handler: BaseHandler,
    fields: dict[str, ArgParseInfo],
    fields_in_section: list[str],
    header_label: str,
    toc_label: str,
    anchor: str,
) -> str:
    """Render a section of cli arguments.

    Args:
        plugin_handler: The plugin handler.
        fields: Collection of all fields.
        fields_in_section: The fields to render in this section.
        header_label: The label for the section header.
        toc_label: The label for the section in the table of contents.
        anchor: The anchor for the section.

    Returns:
        An html string.
    """
    if not fields_in_section:
        return ''
    buffer: list[str] = []
    section_header = plugin_handler.do_heading(
        Markup(header_label),
        heading_level=2,
        toc_label=toc_label,
        id=anchor,
    )
    buffer.append(section_header)
    for field_name in fields_in_section:
        field = fields[field_name]
        names = ', '.join([
            f'<code>{name}</code>' for name in field.option_names
        ])
        toc_names = ', '.join(field.option_names)
        header = plugin_handler.do_heading(
            Markup(names),
            heading_level=3,
            toc_label=toc_names,
            id=field_name,
        )
        extras = []
        if field.default_value:
            extras.append(f'<li>default: <code>{field.default_value}</code></li>')
        if field.choices:
            choices = ', '.join([
                f'<code>{choice}</code>'
                for choice in field.choices
            ])
            extras.append(f'<li>choices: {choices}</li>')
        extras_str = ''.join(extras)
        extras_str = f'<ul>{extras_str}</ul>' if extras else ''
        body = plugin_handler.do_convert_markdown(field.description, 3)
        buffer.append(f'{header}\n{extras_str}\n{body}')
    return '\n'.join(buffer)
