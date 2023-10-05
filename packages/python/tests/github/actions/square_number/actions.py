from m.github.actions import Action

from .main import GithubInputs, main_step

actions = Action(
    name='square_number',
    description='Square a number.',
    file_path='actions.yaml',
    inputs=GithubInputs,
    steps=[
        main_step(
            id='square',
            args=GithubInputs(num='inputs.num'),
        ),
    ]
)
