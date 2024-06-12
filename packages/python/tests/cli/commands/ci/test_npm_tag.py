import pytest
from m.npm.tag import npm_tags
from pydantic import BaseModel
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase, assert_streams, run_cli


@pytest.mark.parametrize('tcase', [
    TCase(cmd=f'm ci npm_tag {m_tag}', expected=expected)
    for m_tag, expected in [
        ('0.0.1', 'latest'),
        ('1.22.333', 'latest'),
        ('0.0.1-pr123.b123', 'pr123'),
        ('0.0.1-rc123.b123', 'next'),
        ('10.0.0-rc123.b123', 'next'),
        ('0.100.0-rc123.b123', 'next'),
        ('0.0.1000-rc123.b123', 'next'),
        ('0.0.1-hotfix123.b123', 'next'),
        ('10.0.0-hotfix123.b123', 'next'),
        ('0.100.0-hotfix123.b123', 'next'),
        ('0.0.1000-hotfix123.b123', 'next'),
        ('99.999.9999-hotfix123.b123', 'next'),
        ('0.0.1-master.b123', 'master'),
        ('0.0.1-develop.b123', 'develop'),
        ('0.0.1-branch.b123', 'branch'),
    ]
])
def test_m_ci_npm_tag(tcase: TCase, mocker: MockerFixture) -> None:
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)


class NpmTagTestCase(BaseModel):
    version: str
    expected: list[str]

@pytest.mark.parametrize('tcase', [
    NpmTagTestCase(version=m_tag, expected=expected)
    for m_tag, expected in [
        ('0.0.1', ['latest']),
        ('1.22.333', ['latest']),
        ('0.0.1-pr123.b123', ['pr123']),
        ('0.0.1-rc123.b123', ['next', 'pr123']),
        ('10.0.0-rc123.b123', ['next', 'pr123']),
        ('0.100.0-rc123.b123', ['next', 'pr123']),
        ('0.0.1000-rc1234.b123', ['next', 'pr1234']),
        ('0.0.1-hotfix123.b123', ['next', 'pr123']),
        ('10.0.0-hotfix123.b123', ['next', 'pr123']),
        ('0.100.0-hotfix123.b123', ['next', 'pr123']),
        ('0.0.1000-hotfix123.b123', ['next', 'pr123']),
        ('99.999.9999-hotfix123.b123', ['next', 'pr123']),
        ('0.0.1-master.b123', ['master']),
        ('0.0.1-develop.b123', ['develop']),
        ('0.0.1-branch.b123', ['branch']),
    ]
])
def test_m_npm_tag(tcase: NpmTagTestCase) -> None:
    result = npm_tags(tcase.version)
    assert result == tcase.expected
