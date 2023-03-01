
from typing import Generic, TypeVar

from pydantic import BaseModel

G_Item = TypeVar('G_Item')


def identity(x: G_Item) -> G_Item:
    """Identity function.

    Args:
        x: The input

    Returns:
        The input value.
    """
    return x


class WithNodes(BaseModel, Generic[G_Item]):
    """An object that may contain nodes."""

    nodes: list[G_Item]
