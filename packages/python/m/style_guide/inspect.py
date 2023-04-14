from m.core import Issue, OneOf, issue, one_of, yaml_fp

from .types import StyleGuideConfig


def read_style_guide(file_name: str) -> OneOf[Issue, StyleGuideConfig]:
    """Read a style guide configuration file.

    Args:
        file_name: The name of the file to read.

    Returns:
        The style guide configuration.
    """
    return one_of(lambda: [
        StyleGuideConfig(**style_guide)
        for style_guide in yaml_fp.read_yson(f'{file_name}.yaml')
    ]).flat_map_bad(lambda x: issue('read_style_guide failure', cause=x))
