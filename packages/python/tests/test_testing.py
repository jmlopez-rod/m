import shutil
from urllib import request as req

import pytest
from m.core import Bad
from m.core.http import fetch


def test_no_internet() -> None:
    prog = None
    with pytest.raises(RuntimeError) as prog_block:
        prog = prog_block
        # pylint: disable-next=consider-using-with
        req.urlopen('https://google.com')  # noqa: S310 - chill out bandit
        # we are making sure no calls are made to the internet
    assert prog and str(prog.value) == 'Network call blocked'


def test_no_internet_fp() -> None:
    res = fetch('https://google.com', {})
    assert isinstance(res, Bad)
    assert 'Network call blocked' in str(res.value)


def test_needs_mocking() -> None:
    err = None
    with pytest.raises(RuntimeError) as err_block:
        err = err_block
        shutil.move('README.md', 'README.md.bak')
    # the following is not a format string
    msg = "shutil.move(('README.md', 'README.md.bak'),{})"  # noqa: P103
    assert err and str(err.value) == f'DEV ERROR: Need to mock {msg}'
