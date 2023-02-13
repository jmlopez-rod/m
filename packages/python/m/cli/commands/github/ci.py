from m.cli import command, run_main
from m.core.io import env
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    r"""Retrieve the information required for continuous integration.

    example::

        $ m github ci \
            --owner jmlopez-rod \
            --repo pysync \
            --sha 4538b2a2556efcbdfc1e7df80c4f71ade45f3958 \
            --pr 1 \
            --include-release | m json
        {
        "commit": {
            "associatedPullRequests": {
            "nodes": [
                {
                "author": {
                    "login": "jmlopez-rod",
                    "avatarUrl": "https://avatars.githubusercontent.com/...",
                    "email": ""
                },
        ...

    NOTE: Use the --merge-commit flag if you are providing a sha from
    github actions.
    """

    owner: str = Field(
        default=env('GITHUB_REPOSITORY_OWNER'),
        description='repo owner',
    )
    repo: str = Field(
        description='repo name',
        required=True,
    )
    sha: str = Field(
        description='commit sha',
        required=True,
    )
    pr: int | None = Field(description='pull request number')
    file_count: int = Field(
        default=10,
        description='max number of files to retrieve',
    )
    include_release: bool = Field(
        default=False,
        description='include the last release information',
    )
    merge_commit: bool = Field(
        default=False,
        description='set if the sha is a merge commit sha (from github)',
    )


@command(
    name='ci',
    help='continuous integration information',
    model=Arguments,
)
def run(arg: Arguments, arg_ns) -> int:
    from m.github.ci import CommitInfo, get_raw_ci_run_info
    return run_main(lambda: get_raw_ci_run_info(
        arg_ns.token,
        CommitInfo(owner=arg.owner, repo=arg.repo, sha=arg.sha),
        arg.pr,
        arg.file_count,
        arg.include_release,
        get_sha=arg.merge_commit,
    ))
