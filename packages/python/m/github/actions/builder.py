import sys
from typing import Any

from m.core import Bad, Good, Res, issue, one_of, rw
from m.pydantic import KebabModel

from .action_file import ActionFile
from .actions import Action
from .system import import_attr


def build_actions(
    actions_py_file: str,
    *,
    check: bool,
    show_traceback: bool,
) -> Res[None]:
    """Create the actions metadata files as described by the actions file.

    Args:
        actions_py_file: The path to a python script containing the actions.
        check: Check if generated files are up to date and skip writing them.
        show_traceback: Display traceback in case of an issue.

    Returns:
        A `Good` containing `None` if the files were written.
    """
    return one_of(lambda: [
        None
        for _ in rw.assert_file_exists(actions_py_file)
        for py_path, actions_module in update_py_path(actions_py_file)
        for possible_actions in import_attr(f'{actions_module}.actions')
        for actions in assert_actions(possible_actions)
        for _ in process_actions(
            py_path,
            actions_module,
            actions,
            check=check,
            show_traceback=show_traceback,
        )
    ])


def update_py_path(actions_py_file: str) -> Res[tuple[str, str]]:
    """Obtain the python path and module name from the actions file.

    It also modifies the PYTHONPATH so that other files may be imported from
    the same directory.

    Args:
        actions_py_file: The path to a python script containing the actions.

    Returns:
        A `Good` containing a tuple of the python path and module name.
    """
    is_file = actions_py_file.endswith('.py')
    parts = actions_py_file.split('/')
    # Need to add the parent directory to the path so that we can do relative
    # imports from the actions file.
    py_path = (
        '/'.join(parts[:-2])
        if is_file
        else '/'.join(parts[:-1])
    )
    sys.path.insert(0, py_path)
    module_name = parts[-1].split('.')[0]
    dir_name = parts[-2] if is_file else ''
    module = f'{dir_name}.{module_name}' if is_file else module_name
    return Good((py_path, module))


def assert_actions(actions: Any) -> Res[list[Action]]:
    """Assert that the actions instance is of type `Action` or `list[Action]`.

    Args:
        actions: The actions instance to assert.

    Returns:
        A `Good` containing a list of `Action`.
    """
    if isinstance(actions, Action):
        return Good([actions])
    if isinstance(actions, list) and all(isinstance(a, Action) for a in actions):
        return Good(actions)
    suggestion = 'ensure all actions are of type "m.github.actions.Action"'
    return issue('invalid_actions', context={'suggestion': suggestion})


def process_actions(
    py_path: str,
    mod_name: str,
    actions: list[Action],
    *,
    check: bool,
    show_traceback: bool,
) -> Res[None]:
    """Iterate over each action to either write or check the action file.

    Args:
        py_path: The root directory of the actions.
        mod_name: The name of the module containing the actions.
        actions: The list of actions to process.
        check: If True, it verifies the action file is up to date.
        show_traceback: Display traceback in case of an issue.

    Returns:
        An `Good` containing None or an issue.
    """
    process_result = [
        process_action(py_path, mod_name, action, check=check)
        for action in actions
    ]
    issues = {
        action.name: action_res.value
        for action_res, action in zip(process_result, actions)
        if isinstance(action_res, Bad)
    }
    if issues:
        return issue(
            'process_actions_failure',
            context={
                'issues': {
                    action_name: iss.to_dict(show_traceback=show_traceback)
                    for action_name, iss in issues.items()
                },
            },
        )
    return Good(None)


def process_action(
    py_path: str,
    actions_module: str,
    action: Action,
    *,
    check: bool,
) -> Res[int]:
    """Process an action to either write or check the action file.

    Args:
        py_path: The root directory of the actions.
        actions_module: The name of the module containing the actions.
        action: The action to process.
        check: If True, it verifies the action file is up to date.

    Returns:
        An `Good` containing None or an issue.
    """
    outputs_res = action.gather_outputs()
    if isinstance(outputs_res, Bad):
        return Bad(outputs_res.value)

    outputs, available_outputs = outputs_res.value
    action_file = ActionFile(
        py_path=py_path,
        module_name=actions_module,
        name=action.name,
        description=action.description,
        inputs=action.inputs or KebabModel,
        action=action,
        outputs=outputs,
        python_path=py_path,
        available_outputs=available_outputs,
    )
    yaml_contents = str(action_file)
    if check:
        current_contents_res = rw.read_file(action.file_path)
        if isinstance(current_contents_res, Bad):
            return Bad(current_contents_res.value)
        current_contents = current_contents_res.value
        if current_contents != yaml_contents:
            return issue(
                'action_file_out_of_date',
                context={
                    'action_name': action.name,
                    'file_path': action.file_path,
                },
            )
        return Good(0)
    return rw.write_file(action.file_path, yaml_contents)
