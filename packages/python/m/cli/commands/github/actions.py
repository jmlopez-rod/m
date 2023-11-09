from m.cli import Arg, BaseModel, command, run_main, validate_file_exists


class Arguments(BaseModel):
    """Create the actions metadata as described by given python script.

    When creating actions we need to have the `python_file` be at the root
    of a python project. This is because when we run the action we will set
    the path to the directory containing the file.

    By default it has been set to `src/actions.py` since this is a common case
    for python projects.

    The `actions.py` can be name anything but it must contain a variable named
    `actions`. This variable must be an instance or list of
    [m.github.actions.Action][].
    """

    python_file: str = Arg(
        default='src/actions.py',
        help='Python script containing the `actions` variable.',
        positional=True,
        validator=validate_file_exists,
    )

    check: bool = Arg(
        default=False,
        help='Check if generated files are up to date and skip writing them.',
    )

    show_traceback: bool = Arg(
        default=False,
        help='Display traceback information in case of an error.',
    )


@command(
    help='create actions metadata',
    model=Arguments,
)
def run(arg: Arguments) -> int:
    from m.github.actions.builder import build_actions

    return run_main(
        lambda: build_actions(
            actions_py_file=arg.python_file,
            check=arg.check,
            show_traceback=arg.show_traceback,
        ),
        result_handler=lambda _: None,
    )
