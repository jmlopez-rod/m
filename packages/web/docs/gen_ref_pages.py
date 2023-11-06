"""Generate the api pages."""
from dataclasses import dataclass
from inspect import cleandoc
from pathlib import Path

import mkdocs_gen_files


@dataclass
class ModuleInfo:
    """Container to store module information."""

    identifier: str
    identifier_paths: tuple[str, ...]
    doc_path: Path
    full_doc_path: Path


def module_file_content(identifier: str) -> str:
    """Generate the content of a module file.

    Args:
        identifier: the module identifier

    Returns:
        The content of the module file.
    """
    file_content = f"""
        ::: {identifier}
            options:
                handler: m_cli
    """
    return cleandoc(file_content)


def api_module_info(src: str, path: Path, root: str) -> ModuleInfo:
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
    full_doc_path = Path(root, doc_path)
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
        doc_path=doc_path,
        full_doc_path=full_doc_path,
    )


def main():
    root = 'api'
    src = '../python'
    nav = mkdocs_gen_files.Nav()

    for path in sorted(Path(src).rglob('*.py')):
        mod_info = api_module_info(src, path, root)
        identifier = mod_info.identifier
        is_m_module = identifier.startswith('m.') or identifier == 'm'
        is_cli = identifier.startswith('m.cli.commands')

        if not identifier or not is_m_module or is_cli:
            continue

        nav[mod_info.identifier_paths] = mod_info.doc_path.as_posix()

        with mkdocs_gen_files.open(mod_info.full_doc_path, 'w') as fd:
            fd.write(module_file_content(identifier))

        mkdocs_gen_files.set_edit_path(mod_info.full_doc_path, Path('../') / path)

    with mkdocs_gen_files.open(f'{root}/SUMMARY.md', 'w') as nav_file:
        nav_file.writelines(nav.build_literate_nav())


main()
