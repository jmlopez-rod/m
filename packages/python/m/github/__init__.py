def compare_sha_url(owner: str, repo: str, prev: str, next_: str) -> str:
    """Provide a url to compare two sha/tags in a github repo."""
    return f'https://github.com/{owner}/{repo}/compare/{prev}...{next_}'
