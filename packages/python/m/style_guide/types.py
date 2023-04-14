from pydantic import BaseModel


class Example(BaseModel):
    """An example in the style guide."""

    # Sample code snippet.
    code: str

    # Expected errors to be raised from the code snippet.
    errors: dict[str, list[tuple[int, int, str]]] | None = None

    # Expected warnings to be raised from the code snippet.
    warnings: dict[str, list[tuple[int, int, str]]] | None = None


class Section(BaseModel):
    """A section in the style guide."""

    # The name of the section.
    name: str

    # A short handle for the section.
    reference: str

    # The order of the section in the style guide.
    sort_order: int = 0

    # A description of the section explaining its purpose.
    rule: str

    # Optional explanation of the rule.
    reason: str | None = None

    # A dictionary mapping a rule name to a url.
    rules: dict[str, str] = {}

    # A list of examples for the section.
    examples: list[dict[str, Example]]


class Topic(BaseModel):
    """A topic in the style guide."""

    # The name of the topic.
    name: str

    # A short handle for the topic.
    reference: str

    # The order of the topic in the style guide.
    sort_order: int

    # A list of sections in the topic.
    sections: list[Section] = []


class StyleGuideConfig(BaseModel):
    """Style guide configuration."""

    # The name of the style guide.
    name: str

    # The description of the style guide.
    description: str

    # Commands applied to all examples in the guide.
    commands: dict[str, str]

    # A list of sections in the style guide.
    topics: list[Topic] = []
