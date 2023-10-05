from m.cli import Arg, BaseModel, command, run_main


class Arguments(BaseModel):
    """Create the actions metadata as described by given python script.

    When creating actions we need to have the `python_file` be at the root
    of a python project. This is because when we run the action we will set
    the path to the directory containing the file.

    By default it has been set to `src/actions.py` since this common case for
    python projects.

    The `actions.py` can be name anything but it must contain a variable named
    `actions`. This variable must be an instance or list of
    `m.github.actions.Action`.
    """

    python_file: str = Arg(
        default='src/actions.py',
        help='python script containing the `actions` variable',
        positional=True,
    )

    check: bool = Arg(
        default=False,
        help='check if generated files are up to date and skip writing them',
    )

    show_traceback: bool = Arg(
        default=False,
        help='Display traceback information in case of an error',
    )


@command(
    help='create actions metadata',
    model=Arguments,
)
def run(arg: Arguments) -> int:
    from m.github.actions.builder import build_actions

    return run_main(
        lambda: build_actions(
            arg.python_file,
            check=arg.check,
            show_traceback=arg.show_traceback,
        ),
        result_handler=lambda _: None,
    )
