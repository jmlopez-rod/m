import pytest
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase, assert_streams, run_cli


@pytest.mark.parametrize('tcase', [
    TCase(cmd=f'm ci npm_tag {m_tag}', expected=expected)
    for m_tag, expected in [
        ('0.0.1', 'latest'),
        ('0.0.1-pr123.b123', 'pr123'),
        ('0.0.1-rc123.b123', 'next'),
        ('0.0.1-hotfix123.b123', 'next'),
        ('0.0.1-master.b123', 'master'),
        ('0.0.1-develop.b123', 'develop'),
        ('0.0.1-branch.b123', 'branch'),
    ]
])
def test_m_ci_npm_tag(tcase: TCase, mocker: MockerFixture) -> None:
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
