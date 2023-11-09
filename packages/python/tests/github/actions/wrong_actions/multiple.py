from pydantic import BaseModel


class MadeUpAction(BaseModel):
    """Some pretend Github action."""

    name: str


actions = [
    MadeUpAction(name='action1'),
    MadeUpAction(name='action2'),
]
