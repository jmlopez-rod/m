from m.cli import Arg, BaseModel, command, run_main
from m.core.io import env


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

    owner: str = Arg(
        default=env('GITHUB_REPOSITORY_OWNER'),
        help='repo owner',
    )
    repo: str = Arg(
        help='repo name',
        required=True,
    )
    sha: str = Arg(
        help='commit sha',
        required=True,
    )
    pr: int | None = Arg(help='pull request number')
    file_count: int = Arg(
        default=10,
        help='max number of files to retrieve',
    )
    include_release: bool = Arg(
        default=False,
        help='include the last release information',
    )
    merge_commit: bool = Arg(
        default=False,
        help='set if the sha is a merge commit sha (from github)',
    )


@command(
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
