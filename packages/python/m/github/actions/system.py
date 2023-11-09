from importlib import import_module
from typing import Any

from m.core import Good, Res, issue


def import_attr(attr_path: str) -> Res[Any]:
    """Get an attribute from a module.

    The `attr_path` should be a fully qualified path to the attribute. For
    example `import_attr('m.core.one_of')` will attempt to retrieve a handle
    on `one_of`.

    Args:
        attr_path: The path to the attribute.

    Returns:
        A `Good` containing the attribute or an issue.
    """
    module_parts = attr_path.split('.')
    module_name = '.'.join(module_parts[:-1])
    item_name = module_parts[-1]
    try:
        module = import_module(module_name)
    except Exception as ex:
        return issue(
            'import_module_failure',
            cause=ex,
            context={'attr_path': attr_path, 'module_name': module_name},
        )
    module_dict = module.__dict__
    if item_name not in module_dict:
        return issue(
            'missing_attribute',
            context={'module': str(module), 'missing_attribute': item_name},
        )
    return Good(module_dict[item_name])
