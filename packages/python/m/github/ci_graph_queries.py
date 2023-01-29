def commit_query(include_pr: bool, include_author: bool) -> str:
    """Build a graphql query for github.

    The output of this function is meant to go inside the repository
    field.

    Args:
        include_pr: If true, it will include pull request information.
        include_author: If true, it will include user information.

    Returns:
        A valid graphql query.
    """
    author = """
      author {
        name
        email
        user {
          login
        }
      }
      oid
    """ if include_author else ''
    pr = """
      associatedPullRequests(first: 1) {
        nodes {
          author {
            login
            avatarUrl(size: 50)
            ... on User {
              email
            }
          }
          number
          title
          body
          baseRefName
          baseRefOid
          headRefName
          headRefOid
          merged
        }
      }
    """ if include_pr else ''
    return f"""
      commit: object(expression: $sha) {{
        ... on Commit {{
          message
          {author}
          {pr}
        }}
      }}
    """


LATEST_RELEASE = """
  releases(last: 1, orderBy: {field: CREATED_AT, direction: ASC}) {
    nodes {
      name
      tagName
      publishedAt
    }
  }
"""

PULL_REQUEST = """
  pullRequest(number: $pr) {
    headRefName
    headRefOid
    baseRefName
    baseRefOid
    title
    body
    url
    author {
      login
      avatarUrl(size: 50)
      ... on User {
        email
      }
    }
    files(first: $fc) {
      totalCount
      nodes {
        path
      }
    }
    merged
    isDraft
  }
"""
