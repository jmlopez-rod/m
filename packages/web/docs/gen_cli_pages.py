"""Generate the code cli pages."""
import inspect
from importlib import import_module
from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()


src = '../python'
all_paths = sorted(Path(src).rglob("*.py"))
new_sort = sorted(all_paths, key=lambda x: len(x.parts))
for path in new_sort:  #
    module_path = path.relative_to(src).with_suffix("")  #
    doc_path = path.relative_to(src).with_suffix(".md")  #

    md_path_parts = doc_path.parts
    md_path = '/'.join(md_path_parts[3:])
    full_doc_path = Path("cli", md_path)  #
    parts = list(module_path.parts)

    if parts[0] != 'm':
        continue


    if parts[-1] == "__init__":  #
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == '__main__':
        continue

    identifier = ".".join(parts)
    if not identifier.startswith('m.cli.commands'):
        continue

    mod_handle = import_module(identifier)
    if not hasattr(mod_handle, 'Arguments'):
        continue

    name = ' '.join(parts[3:])
    nav[parts[3:]] = Path(md_path).as_posix()

    # print('module:', repr(parts))
    # if '.'.join(parts) not in 'm.ci.release_env.ReleaseEnv':
    #     continue
    ArgModel = mod_handle.Arguments
    show_base = len(inspect.getmro(ArgModel)) > 3

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        print(f'# m {name}', file=fd)
        print(f"::: {identifier}.Arguments", file=fd)  #
        print("    options:", file=fd)
        print("      is_command: true", file=fd)
        print(f"      show_bases: {show_base}", file=fd)
        print("      show_root_toc_entry: false", file=fd)
        print("      show_root_full_path: false", file=fd)
        print("      handler: m_cli", file=fd)

    # print(mkdocs_gen_files.open(full_doc_path, "r").read())

    mkdocs_gen_files.set_edit_path(full_doc_path, Path("../") / path)  #


with mkdocs_gen_files.open("cli/SUMMARY.md", "w") as nav_file:  #
    nav_file.writelines(nav.build_literate_nav())
