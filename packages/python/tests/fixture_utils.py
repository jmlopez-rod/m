def read_fixture(name: str, path: str) -> str:
    """Read a fixture file from a given path.

    Args:
        name: The name of the fixture file.
        path: The directory of the fixture relative to the tests directory.

    Returns:
        The contents of the file.
    """
    fname = f'./packages/python/tests/{path}/{name}'
    with open(fname, encoding='UTF-8') as fp:
        return fp.read()
