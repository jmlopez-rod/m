from m.github.actions import Action

from .gha_one_step import ExternalActionInputs, gha_one_step
from .main import MainInputs, main_step
from .models import GithubInputs
from .no_args import no_args_step
from .setup import SetupInputs, setup_step

actions = [
    Action(
        file_path='multiple/action.yaml',
        name='Made Up Action',
        description='Main description.',
        inputs=GithubInputs,
        steps=[
            setup_step('setup', SetupInputs(
                setup_in_1='inputs.arg_1',
                setup_in_2="pnpm-store-${{ hashFiles('**/pnpm-lock.yaml') }}",
            )),
            gha_one_step('external', ExternalActionInputs(
                external_in='setup.setup_out_1',
            )),
            main_step('main', MainInputs(
                main_in='external.external_2',
            )),
        ],
    ),
    Action(
        file_path='multiple/action-empty.yaml',
        name='No Inputs No Outputs',
        description='No args description.',
        inputs=None,
        steps=[no_args_step('no_args')],
    ),
]

actions_bad_inputs = [
    Action(
        file_path='multiple/action.yaml',
        name='Made Up Action',
        description='Main description.',
        inputs=GithubInputs,
        steps=[
            setup_step('setup', SetupInputs(
                setup_in_1='inputs.arg-1',
                setup_in_2='inputs.arg_2',
            )),
            gha_one_step('external', ExternalActionInputs(
                external_in='setup.not-real',
            )),
            main_step('main', MainInputs(
                main_in="pnpm-store-${{ hashFiles('**/pnpm-lock.yaml') }}",
            )),
        ],
    ),
]
