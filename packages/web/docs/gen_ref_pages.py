"""Generate the code reference pages."""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

src = '../python'
for path in sorted(Path(src).rglob("*.py")):  #
    module_path = path.relative_to(src).with_suffix("")  #
    doc_path = path.relative_to(src).with_suffix(".md")  #
    full_doc_path = Path("reference", doc_path)  #
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
    if identifier.startswith('m.cli'):
        continue

    nav[parts] = doc_path.as_posix()

    # print('module:', repr(parts))
    # if '.'.join(parts) not in 'm.ci.release_env.ReleaseEnv':
    #     continue

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:  #
        print("::: " + identifier, file=fd)  #
        print("    options:", file=fd)
        print("      handler: m_cli", file=fd)

    # print(mkdocs_gen_files.open(full_doc_path, "r").read())

    mkdocs_gen_files.set_edit_path(full_doc_path, Path("../") / path)  #


with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:  #
    nav_file.writelines(nav.build_literate_nav())
