from pathlib import Path
from typing import Any, Mapping

from griffe.dataclasses import Class as GriffeClass
from griffe.dataclasses import Module as GriffeModule
from mkdocstrings.handlers.base import CollectorItem
from mkdocstrings_handlers.python.handler import PythonHandler
from pydantic import BaseModel

from .class_attr import attach_attributes
from .field_parser import ArgParseInfo, CliArgs, parse_field
from .render_arg import render_cli_arguments


class MCLIHandler(PythonHandler):
    """The m_cli handler class."""

    models: dict[int, BaseModel] = {}

    def get_templates_dir(self, handler: str | None = None) -> Path:  # noqa: WPS110
        """Return the path to the PythonHandler's templates directory.

        Arguments:
            handler: The name of the handler to get the templates directory of.

        Returns:
            The templates directory path.
        """
        return super().get_templates_dir('python')

    def collect(
        self,
        identifier: str,
        config: Mapping[str, Any],
    ) -> CollectorItem:
        """Add attributes to the docstring.

        This only happens if we are not dealing with an `m` cli command.

        Args:
            identifier: The identifier of the object to collect.
            config: The configuration passed to the handler.

        Returns:
            The collected object.
        """
        griffe_obj = PythonHandler.collect(self, identifier, config)
        if isinstance(griffe_obj, GriffeModule):
            for member_name, member in griffe_obj.members.items():
                if isinstance(member, GriffeClass):
                    class_identifier = f'{identifier}.{member_name}'
                    self._process_class(member, class_identifier, config)
        if isinstance(griffe_obj, GriffeClass):
            self._process_class(griffe_obj, identifier, config)
        return griffe_obj

    def render(
        self,
        data: CollectorItem,  # noqa: WPS110 - name in parent class
        config: Mapping[str, Any],
    ) -> str:
        """Render the docstring of an object.

        Args:
            data: The object to render.
            config: The configuration passed to the handler.

        Returns:
            An html string.
        """
        model = self.models.get(id(data))
        base_str = PythonHandler.render(self, data, config)
        if not config.get('is_command', False) or not model:
            return base_str

        fields: dict[str, ArgParseInfo] = {
            field_name: parse_field(field_name, field)
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
            render_cli_arguments(
                self,
                fields,
                args.required,
                'Required arguments',
                'Required arguments',
                'required-arguments',
            ),
            render_cli_arguments(
                self,
                fields,
                args.optional,
                'Options',
                'Options',
                'options',
            ),
            render_cli_arguments(
                self,
                fields,
                args.positional,
                'Positional arguments',
                'Positional arguments',
                'positional-arguments',
            ),
        ]
        filtered = [block for block in doc_content if block]
        return base_str + '\n'.join(filtered)

    def _process_class(
        self,
        griffe_class: GriffeClass,
        identifier: str,
        config: Mapping[str, Any],
    ) -> None:
        obj_id = id(griffe_class)
        if obj_id not in self.models:
            arg_model = attach_attributes(griffe_class, identifier, config)
            self.models[obj_id] = arg_model


def get_handler(  # noqa: WPS211
    *,
    theme: str,
    custom_templates: str | None = None,
    config_file_path: str | None = None,
    paths: list[str] | None = None,
    locale: str = 'en',
    load_external_modules: bool = False,
    **kwargs: Any,  # noqa: ARG001
) -> MCLIHandler:
    """Create an instance of an `MCLIHandler`.

    Args:
        theme: The theme to use when rendering contents.
        custom_templates: Directory containing custom templates.
        config_file_path: The MkDocs configuration file path.
        paths: A list of paths to use as Griffe search paths.
        locale: The locale to use when rendering content.
        load_external_modules: Load external modules when resolving aliases.
        kwargs: Configuration passed to the handler.

    Returns:
        An instance of `MCLIHandler`.
    """
    return MCLIHandler(
        handler='m_cli',
        theme=theme,
        custom_templates=custom_templates,
        config_file_path=config_file_path,
        paths=paths,
        locale=locale,
        load_external_modules=load_external_modules,
    )
