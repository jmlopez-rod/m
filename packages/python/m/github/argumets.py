import re

from m.git import get_remote_url
from pydantic import BaseModel, Field


def repo_and_owner():
    repository_url = get_remote_url()

    if repository_url.is_bad:
        return None, None

    repository_url_parser = re.compile(r"((?:https?:\/\/)|(?:\w+@))github\.com[:\/]([^\/]+)\/([^\/]+)\.git")

    match = repository_url_parser.match(repository_url.value)

    if match is None:
        return None, None

    _, owner, repo = match.groups()

    return owner, repo

owner, repo = repo_and_owner()

class RepoAndOwnerArgs(BaseModel):
    owner: str = Field(
        default=owner,
        description='repo owner',
    )
    repo: str = Field(
        default=repo,
        description='repo name',
    )
