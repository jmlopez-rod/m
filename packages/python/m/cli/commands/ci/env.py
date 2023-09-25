from m.cli import (
    Arg,
    BaseModel,
    command,
    create_json_handler,
    create_yaml_handler,
    run_main,
)


class Arguments(BaseModel):
    """Create the [m_dir]/.m/env.list file.

    With the `bashrc` option it will print a bashrc snippet and no file will
    be created. Note that boolean values are lowercased in the snippet. This
    eventually be the case for generated env.list file.
    """

    pretty: bool = Arg(
        default=False,
        help='format json payload with indentation',
    )
    yaml: bool = Arg(
        default=False,
        help='use yaml format',
    )
    m_dir: str = Arg(
        default='m',
        help='m project directory',
        positional=True,
    )
    bashrc: bool = Arg(
        default=False,
        help='print bashrc snippet',
    )


@command(
    help='create a list of env variables',
    model=Arguments,
)
def run(arg: Arguments) -> int:
    from m.ci.m_env import bashrc_snippet, write_m_env_vars

    if arg.bashrc:
        return run_main(
            lambda: bashrc_snippet(arg.m_dir),
            result_handler=print,
        )

    result_handler = (
        create_yaml_handler(arg.pretty)
        if arg.yaml
        else create_json_handler(arg.pretty)
    )
    return run_main(
        lambda: write_m_env_vars(arg.m_dir),
        result_handler=result_handler,
    )
