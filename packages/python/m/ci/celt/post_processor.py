from typing import Dict

from ...core import Good, Issue, OneOf, issue
from .core.process import PostProcessor
from .core.types import Configuration, Transform
from .post_processors import eslint, pycodestyle, pylint, typescript


def get_post_processor(
    name: str,
    celt_config: Configuration,
) -> OneOf[Issue, PostProcessor]:
    """Find an available post processor based on the key provided.

    Args:
        name: name of the post processor
        celt_config: The configuration to use

    Returns:
        A `OneOf` containing an `Issue` or a post processor function.
    """
    mapping: Dict[str, Transform] = {
        'eslint': eslint.read_payload,
        'pycodestyle': pycodestyle.read_payload,
        'flake8': pycodestyle.read_payload,
        'pylint': pylint.read_payload,
        'typescript': typescript.read_payload,
    }
    if name not in mapping:
        return issue(f'{name} is not a supported post processor')

    return Good(PostProcessor(name, celt_config, mapping[name]))
