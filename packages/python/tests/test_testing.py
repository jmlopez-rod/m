import urllib.request as req
from pathlib import Path

import pytest
from m.core import Bad
from m.core.http import fetch


def test_no_internet() -> None:
    prog = None
    with pytest.raises(RuntimeError) as prog_block:
        prog = prog_block
        req.urlopen('https://google.com')
    assert prog and str(prog.value) == 'Network call blocked'


def test_no_internet_fp() -> None:
    res = fetch('https://google.com', {})
    assert isinstance(res, Bad)
    assert 'Network call blocked' in str(res.value)


def test_needs_mocking() -> None:
    err = None
    path = Path('do-not-create-please')
    with pytest.raises(RuntimeError) as err:
        path.mkdir()
    msg = "pathlib.Path.mkdir((),{})"
    assert err and str(err.value) == f'DEV ERROR: Need to mock {msg}'
