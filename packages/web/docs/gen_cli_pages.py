"""Generate the code cli pages."""
import inspect
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path

import mkdocs_gen_files


@dataclass
class ModuleInfo:
    """Container to store module information."""

    identifier: str
    identifier_paths: tuple[str, ...]
    doc_path: Path
    full_doc_path: Path


def cli_command_file_content(
    identifier: str,
    name: str,
    show_base: bool,
) -> str:
    """Generate the content of a cli command file.

    Args:
        identifier: the module identifier
        name: the name of the command
        show_base: whether to show the base classes

    Returns:
        The content of the module file.
    """
    file_content = f"""\
        # m {name}
        ::: {identifier}.Arguments
            options:
              handler: m_cli
              is_command: true
              show_bases: {show_base}
              show_root_toc_entry: false
              show_root_full_path: false
    """
    return inspect.cleandoc(file_content)


def cli_module_info(src: str, path: Path, root: str) -> ModuleInfo:
    """Create the identifier for a module.

    Args:
        src: the source directory
        path: the module path
        root: the root package - the base path in the url.

    Returns:
        The module identifier or an empty string.
    """
    module_path = path.relative_to(src).with_suffix('')
    doc_path = path.relative_to(src).with_suffix('.md')
    md_path_parts = doc_path.parts
    md_path = '/'.join(md_path_parts[3:])
    full_doc_path = Path(root, md_path)
    parts = list(module_path.parts)

    if parts[-1] == '__init__':
        parts = parts[:-1]
        doc_path = doc_path.with_name('index.md')
        full_doc_path = full_doc_path.with_name('index.md')
    elif parts[-1] == '__main__':
        parts = []

    return ModuleInfo(
        identifier='.'.join(parts),
        identifier_paths=tuple(parts),
        doc_path=Path(md_path),
        full_doc_path=full_doc_path,
    )


def main():
    root = 'cli'
    src = '../python'
    nav = mkdocs_gen_files.Nav()

    all_paths = sorted(Path(src).rglob('*.py'))
    new_sort = sorted(all_paths, key=lambda x: len(x.parts))
    for path in new_sort:
        mod_info = cli_module_info(src, path, root)
        identifier = mod_info.identifier
        is_cli = identifier.startswith('m.cli.commands')

        if not is_cli:
            continue

        mod_handle = import_module(identifier)
        if not hasattr(mod_handle, 'Arguments'):  # noqa: WPS421 - ask first
            continue

        name = ' '.join(mod_info.identifier_paths[3:])
        nav[mod_info.identifier_paths[3:]] = mod_info.doc_path.as_posix()

        arg_model = mod_handle.Arguments
        show_base = len(inspect.getmro(arg_model)) > 3

        with mkdocs_gen_files.open(mod_info.full_doc_path, 'w') as fd:
            fd.write(cli_command_file_content(identifier, name, show_base))

        mkdocs_gen_files.set_edit_path(mod_info.full_doc_path, Path('../') / path)

    with mkdocs_gen_files.open(f'{root}/SUMMARY.md', 'w') as nav_file:
        nav_file.writelines(nav.build_literate_nav())


main()
