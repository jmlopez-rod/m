import pytest
from m.ci.config import Config, GitFlowConfig, MFlowConfig, Workflow
from m.core import Good
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import assert_streams, run_cli

base_config = Config(
    owner='owner',
    repo='repo',
    version='0.0.0',
    m_dir='m',
    workflow=Workflow.free_flow,
    git_flow=GitFlowConfig(),
    m_flow=MFlowConfig(),
)


class TCase(CliTestCase):
    """Test case for `m ci bump_version`."""

    config_mock: Config
    git_branch: str


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd='m ci assert_branch --type release m',
        config_mock=base_config.copy(update={
            'workflow': 'oops',
        }),
        git_branch='master',
        errors=['invalid m workflow'],
        exit_code=1,
    ),
])
def test_m_ci_assert_branch(tcase: TCase, mocker: MockerFixture) -> None:
    read_config = mocker.patch('m.ci.config.read_config')
    read_config.return_value = Good(tcase.config_mock)
    get_branch = mocker.patch('m.git.get_branch')
    get_branch.return_value = Good(tcase.git_branch)
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
