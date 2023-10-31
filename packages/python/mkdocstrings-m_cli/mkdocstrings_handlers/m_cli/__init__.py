
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any, Mapping, cast

from griffe.dataclasses import Class as GriffeClass
from griffe.dataclasses import Docstring
from markupsafe import Markup
from mkdocstrings.handlers.base import CollectorItem
from mkdocstrings_handlers.python.handler import PythonHandler
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

AnyMap = dict[str, Any]
MISSING = PydanticUndefined

@dataclass
class CliArgs:
    positional: list[str]
    optional: list[str]
    required: list[str]


def argument_name(name: str) -> str:
    """Normalize an argument name.

    Args:
        name: Name of the argument.

    Returns:
        Normalized name of the argument.
    """
    cli_arg_name = name.replace('_', '-')
    dashes = '-' if len(cli_arg_name) == 1 else '--'
    return f'{dashes}{cli_arg_name}'


@dataclass
class FuncArgs:
    """Stores function arguments."""

    args: list[Any]
    kwargs: dict[str, Any]

class ArgParseInfo(BaseModel):
    """Information about an argparse argument."""

    description: str
    option_names: list[str]
    choices: None | list[str]
    default_value: None | str
    required: bool = False
    positional: bool = False

def _parse_info_bool(name: str, field: FieldInfo) -> ArgParseInfo:
    """Treat the field as a boolean field.

    Args:
        name: The name of the argument.
        field: A dictionary representation of the field.

    Returns:
        Function arguments for the parser `add_argument` method.
    """
    default = field.default
    extras = cast(dict, field.json_schema_extra or {})
    aliases = cast(list[str], extras.get('aliases', None))
    if default:
        names = [argument_name(f'no-{name}')]
        if aliases:
            names = [argument_name(f'no-{alias}') for alias in aliases]
    else:
        names = [argument_name(name)]
        if aliases:
            names = [argument_name(alias) for alias in aliases]

    return ArgParseInfo(
        description=field.description or '',
        option_names=names,
        choices=None,
        default_value=str(bool(default)).lower(),
    )


def _parse_info_standard(name: str, field: FieldInfo) -> ArgParseInfo:
    extras = cast(dict, field.json_schema_extra or {})
    default = field.default
    required = extras.get('required', False)
    aliases = cast(list[str], extras.get('aliases', None))



    names = [argument_name(name)]
    if aliases:
        names = [argument_name(alias) for alias in aliases]

    return ArgParseInfo(
        description=field.description or '...',
        option_names=names,
        choices=None,
        default_value=None if default is MISSING else repr(default),
        required=required,
    )


def _parse_field(name: str, field: FieldInfo) -> ArgParseInfo:
    extras = field.json_schema_extra
    default = field.default
    if not isinstance(extras, dict):  # pragma: no cover
        not_supported = 'json_schema_extra only supported as a dict'
        raise NotImplementedError(not_supported)
    if extras.get('positional', False) is True:
        return ArgParseInfo(
            description=field.description or '...',
            option_names=[name],
            choices=None,
            default_value=None if default is MISSING else repr(default),
            positional=True,
        )
    if field.annotation is bool:
        return _parse_info_bool(name, field)
    if extras.get('proxy', None) is not None:
        proxy = cast(FuncArgs, extras['proxy'])
        return ArgParseInfo(
            description=proxy.kwargs.get('help', '...'),
            option_names=proxy.args,
            choices=proxy.kwargs.get('choices', None),
            default_value=proxy.kwargs.get('default', None),
        )
    if extras.get('__remainder_args') is True:
        return ArgParseInfo(
            description=field.description or '...',
            option_names=[name],
            choices=None,
            default_value=None if default is MISSING else repr(default),
        )
    return _parse_info_standard(name, field)


def import_attr(attr_path: str) -> Any:
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
    module = import_module(module_name)
    module_dict = module.__dict__
    return module_dict[item_name]


class MCLIHandler(PythonHandler):
    models: dict[int, BaseModel] = {}

    def __init__(
        self,
        *args: Any,
        config_file_path: str | None = None,
        paths: list[str] | None = None,
        locale: str = "en",
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

    def get_templates_dir(self, handler: str | None = None) -> Path:
        return super().get_templates_dir('python')

    def collect(self, identifier: str, config: Mapping[str, Any]) -> CollectorItem:  # noqa: D102
        """Extend the default `collect` method to add attributes to the docstring.

        This only happens if we are not dealing with a command.

        Args:
            identifier: The identifier of the object to collect.
            config: The configuration passed to the handler.

        Returns:
            The collected object.
        """
        obj = PythonHandler.collect(self, identifier, config)
        if not isinstance(obj, GriffeClass):
            return obj
        obj_id = id(obj)
        arg_model = cast(BaseModel, import_attr(identifier))
        if not obj_id in self.models:
            self.models[obj_id] = arg_model
            is_command = config.get('is_command', False)
            if not is_command and hasattr(arg_model, 'model_fields') and obj.docstring:
                att_str = '\n    '.join([
                    f'{field}: {field_info.description or "..."}'
                    for field, field_info in arg_model.model_fields.items()
                ])
                to_add = f'\n\nAttributes:\n    {att_str}'
                obj.docstring = Docstring(
                    value=f'{obj.docstring.value}{to_add}',
                    lineno=obj.docstring.lineno,
                    endlineno=obj.docstring.endlineno,
                    parent=obj.docstring.parent,
                    parser=obj.docstring.parser,
                    parser_options=obj.docstring.parser_options,
                )
        return obj

    def _process_cli_section(
        self,
        fields: dict[str, ArgParseInfo],
        fields_in_section: list[str],
        header_label: str,
        toc_label: str,
        anchor: str,
    ) -> str:
        if not fields_in_section:
            return ''
        buffer: list[str] = []
        section_header = self.do_heading(
            Markup(header_label),
            heading_level=2,
            toc_label=toc_label,
            id=anchor,
        )
        buffer.append(section_header)
        for field_name in fields_in_section:
            field = fields[field_name]
            names = ', '.join([
                f'<code>{name}</code>' for name in field.option_names
            ])
            toc_names = ', '.join(field.option_names)
            header = self.do_heading(
                Markup(names),
                heading_level=3,
                toc_label=toc_names,
                id=field_name,
            )
            extras = []
            if field.default_value:
                extras.append(f'<li>default: <code>{field.default_value}</code></li>')
            if field.choices:
                choices = ', '.join([
                    f'<code>{choice}</code>'
                    for choice in field.choices
                ])
                extras.append(f'<li>choices: {choices}</li>')
            extras_str = '<ul>' + ''.join(extras) + '</ul>' if extras else ''
            body = self.do_convert_markdown(field.description, 3)
            buffer.append(f'{header}\n{extras_str}\n{body}')
        return '\n'.join(buffer)


    def render(self, data: CollectorItem, config: Mapping[str, Any]) -> str:  # noqa: D102 (ignore missing docstring)
        base_str = PythonHandler.render(self, data, config)
        model = self.models.get(id(data))
        if not config.get('is_command', False) or not model:
            return base_str

        fields: dict[str, ArgParseInfo] = {
            field_name: _parse_field(field_name, field)
            for field_name, field in model.model_fields.items()
        }
        args = CliArgs(
            positional=[
                field_name
                for field_name, field in fields.items()
                if field.positional
            ],
            optional=[
                field_name
                for field_name, field in fields.items()
                if not field.positional and not field.required
            ],
            required=[
                field_name
                for field_name, field in fields.items()
                if not field.positional and field.required
            ],
        )

        doc_content: list[str] = [
            self._process_cli_section(
                fields,
                args.required,
                'Required arguments',
                'Required arguments',
                'required-arguments',
            ),
            self._process_cli_section(
                fields,
                args.optional,
                'Options',
                'Options',
                'options',
            ),
            self._process_cli_section(
                fields,
                args.positional,
                'Positional arguments',
                'Positional arguments',
                'positional-arguments',
            ),
        ]
        filtered = [item for item in doc_content if item]
        return base_str + '\n'.join(filtered)


def get_handler(
    theme: str,
    custom_templates: str | None = None,
    config_file_path: str | None = None,
    paths: list[str] | None = None,
    locale: str = "en",
    load_external_modules: bool = False,
    **config: Any,  # noqa: ARG001
) -> MCLIHandler:
    """Simply return an instance of `PythonHandler`.

    Arguments:
        theme: The theme to use when rendering contents.
        custom_templates: Directory containing custom templates.
        config_file_path: The MkDocs configuration file path.
        paths: A list of paths to use as Griffe search paths.
        locale: The locale to use when rendering content.
        **config: Configuration passed to the handler.

    Returns:
        An instance of `PythonHandler`.
    """
    return MCLIHandler(
        handler="m_cli",
        theme=theme,
        custom_templates=custom_templates,
        config_file_path=config_file_path,
        paths=paths,
        locale=locale,
        load_external_modules=load_external_modules,
    )
