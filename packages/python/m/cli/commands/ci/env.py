from m.cli import (
    Arg,
    BaseModel,
    command,
    create_json_handler,
    create_yaml_handler,
    run_main,
)


class Arguments(BaseModel):
    """Create the [m_dir]/.m/env.list file."""

    pretty: bool = Arg(
        default=False,
        help='format json payload with indentation',
    )
    yaml: bool = Arg(
        default=False,
        help='use yaml format',
    )
    m_dir: str = Arg(
        help='m project directory',
        positional=True,
        required=True,
    )


@command(
    help='create a list of env variables',
    model=Arguments,
)
def run(arg: Arguments) -> int:
    from m.ci.m_env import write_m_env_vars

    result_handler = (
        create_yaml_handler(arg.pretty)
        if arg.yaml
        else create_json_handler(arg.pretty)
    )
    return run_main(
        lambda: write_m_env_vars(arg.m_dir),
        result_handler=result_handler,
    )
