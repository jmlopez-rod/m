from collections import OrderedDict
from typing import Any, cast

import yaml

tag_prefix = 'tag:yaml.org,2002'


def _ordered_dict_presenter(dumper: yaml.SafeDumper, py_data: OrderedDict):
    return dumper.represent_mapping(f'{tag_prefix}:map', py_data.items())


def _tuple_presenter(dumper: yaml.SafeDumper, py_data: tuple):
    return dumper.represent_sequence(f'{tag_prefix}:seq', py_data)


def _str_presenter(dumper: yaml.SafeDumper, py_data: str):
    if '\n' in py_data:  # check for multiline string
        # tab characters do not play along with yaml
        # found this when trying to print the output of `git status`.
        return dumper.represent_scalar(
            f'{tag_prefix}:str',
            py_data.replace('\r\n', '\n').replace('\t', '    '),
            style='|',
        )
    return dumper.represent_scalar(f'{tag_prefix}:str', py_data)


yaml.add_representer(
    OrderedDict,
    _ordered_dict_presenter,
    Dumper=yaml.SafeDumper,
)
yaml.add_representer(tuple, _tuple_presenter, Dumper=yaml.SafeDumper)
yaml.add_representer(str, _str_presenter, Dumper=yaml.SafeDumper)


def dumps(py_data: Any) -> str:
    """Dump data as yaml using the safe_dump method.

    Args:
        py_data: Any object that may be serialized.

    Returns:
        A yaml serialized string.
    """
    return cast(str, yaml.safe_dump(py_data))
