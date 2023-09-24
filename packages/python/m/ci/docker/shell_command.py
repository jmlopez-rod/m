from pydantic import BaseModel


def _to_opt(option: str) -> str:
    opt = option.replace('_', '-', -1)
    if opt.startswith('--'):
        return opt
    return f'--{opt}'


def _to_list(options: dict[str, str | list[str] | bool]) -> list[str]:
    """Convert a dict to a list of strings.

    Args:
        options: The dict to convert.

    Returns:
        A list of strings.
    """
    options_list: list[str] = []
    standard_opts = {_to_opt(key): opt_val for key, opt_val in options.items()}
    for opt_name in sorted(standard_opts):
        opt_val = standard_opts[opt_name]
        if isinstance(opt_val, list):
            for opt_val_item in opt_val:
                options_list.append(f'{opt_name} {opt_val_item}')
        elif isinstance(opt_val, bool) and opt_val:
            options_list.append(opt_name)
        else:
            options_list.append(f'{opt_name} {opt_val}')
    return sorted(options_list)


class ShellCommand(BaseModel):
    """Representation of a shell command."""

    # Name of the program to run. May contain spaces if the program is a subcommand.
    prog: str

    # Arguments to pass to the program.
    # If the key starts with `--` it will be passed as is. Otherwise it will be
    # considered as a python property and will be passed as `--key`.
    options: dict[str, str | list[str] | bool] = {}

    # Positional arguments to pass to the program.
    positional: list[str] = []

    def __str__(self) -> str:
        """Render the command as a string.

        A new line is not added to the end of the string in case the command
        needs to be piped to another command.

        Returns:
            A string representation of the command.
        """
        lines = [self.prog, *_to_list(self.options), *self.positional]
        # We need to join with a backslash and a new line.
        return' \\\n  '.join(lines)  # noqa: WPS342
