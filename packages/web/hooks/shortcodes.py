"""
Modified version from:

https://github.com/squidfunk/mkdocs-material/blob/master/src/overrides/hooks/shortcodes.py

All we are currently interested is in being able to insert a version badge

<!-- md:version 1.2.3 -->

Which will link to the changelog in this documentation site.
"""
import posixpath
import re
from functools import partial
from re import Match

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page


def _replace_version(page: Page, files: Files, match: Match):
    type, args = match.groups()
    args = args.strip()
    if type == "version":
        return _badge_for_version(args, page, files)

    # Otherwise, raise an error
    raise RuntimeError(f"Unknown shortcode: {type}")


def on_page_markdown(
    markdown: str,
    *,
    page: Page,
    config: MkDocsConfig,
    files: Files
) -> str:
    """Hook to execute after markdown is loaded from file.

    https://www.mkdocs.org/dev-guide/plugins/#on_page_markdown

    See: https://www.mkdocs.org/user-guide/configuration/#hooks
    """
    replace = partial(_replace_version, page, files)
    return re.sub(
        r"<!-- md:(\w+)(.*?) -->",
        replace, markdown, flags = re.I | re.M
    )


# Resolve path of file relative to given page - the posixpath always includes
# one additional level of `..` which we need to remove
def _resolve_path(path: str, page: Page, files: Files):
    path, anchor, *_ = f"{path}#".split("#")
    file = files.get_file_from_path(path)
    if not file:
        raise RuntimeError(f"File not found: {path}")
    path = _resolve(file, page)
    return "#".join([path, anchor]) if anchor else path

# Resolve path of file relative to given page - the posixpath always includes
# one additional level of `..` which we need to remove
def _resolve(file: File, page: Page):
    path = posixpath.relpath(file.src_uri, page.file.src_uri)
    return posixpath.sep.join(path.split(posixpath.sep)[1:])


# Create badge
def _badge(icon: str, text: str = "", type: str = ""):
    classes = f"mdx-badge mdx-badge--{type}" if type else "mdx-badge"
    return "".join([
        f"<span class=\"{classes}\">",
        *([f"<span class=\"mdx-badge__icon\">{icon}</span>"] if icon else []),
        *([f"<span class=\"mdx-badge__text\">{text}</span>"] if text else []),
        '</span>',
    ])


# Create badge for version
def _badge_for_version(text: str, page: Page, files: Files):
    spec = text
    path = f"changelog.md#{spec}"
    icon = "material-tag-outline"
    return _badge(
        icon = f":{icon}:",
        text = f"[{text}]({_resolve_path(path, page, files)})" if spec else ""
    )
