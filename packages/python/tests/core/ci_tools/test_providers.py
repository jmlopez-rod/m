import json
import logging
import os
import sys
from io import StringIO
from textwrap import dedent
from typing import cast

from m.core import Issue
from m.log import EnvVars, Logger, get_ci_tool, logging_config
from pytest_mock import MockerFixture

logger = Logger('test.providers')
no_color = {'NO_COLOR': 'true'}


def mock_streams(mocker: MockerFixture):
    std_out = StringIO()
    std_err = StringIO()
    log_hdl = StringIO()
    mocker.patch('logging.FileHandler._open').return_value = log_hdl
    mocker.patch('time.time').return_value = 123456789
    mocker.patch.object(sys, 'stdout', std_out)
    mocker.patch.object(sys, 'stderr', std_err)
    return std_out, std_err, log_hdl


def test_ci_tool_warn_block(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, no_color, clear=True)
    std_out, std_err, _ = mock_streams(mocker)
    logging_config()
    logger.waning_block('some warning', {'context': []})
    assert std_out.getvalue() == ''
    assert std_err.getvalue() == dedent("""\
        [WARNING] [09:33:09 PM - Nov 29, 1973]: some warning
          >>> [warning]:
                    {
                      "context": []
                    }

    """)


def test_ci_tool_close_blocks(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, no_color, clear=True)
    std_out, std_err, _ = mock_streams(mocker)
    logging_config()
    logger.info('a')
    logger.open_block('b1', 'open b1')
    logger.open_block('b2', 'open b2')
    logger.info('b')
    logger.close_block('b1')
    logger.info('c')
    assert std_err.getvalue() == ''
    assert std_out.getvalue() == dedent("""\
        [INFO] [09:33:09 PM - Nov 29, 1973]: a
          >>> [b1]: open b1
            >>> [b2]: open b2
            [INFO] [09:33:09 PM - Nov 29, 1973]: b

        [INFO] [09:33:09 PM - Nov 29, 1973]: c
    """)


def test_ci_tool_json_logger(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, no_color, clear=True)
    std_out, std_err, log_hdl = mock_streams(mocker)
    logging_config(json_file='file_log.json')
    logger.info('a')
    logger.debug('should not display')
    logger.info('b', {'info': 'b_value'})
    assert std_err.getvalue() == ''
    assert std_out.getvalue() == dedent("""\
        [INFO] [09:33:09 PM - Nov 29, 1973]: a
        [INFO] [09:33:09 PM - Nov 29, 1973]: b
               {
                 "info": "b_value"
               }
    """)
    file_log = log_hdl.getvalue()
    lines = [json.loads(line) for line in file_log.splitlines()]
    assert len(lines) == 2
    assert lines[0].get('msg') == 'a'
    assert lines[1].get('msg') == 'b'
    assert lines[1].get('context').get('info') == 'b_value'


def test_ci_tool_json_logger_debug(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, no_color, clear=True)
    std_out, std_err, log_hdl = mock_streams(mocker)
    logging_config(level=logging.DEBUG, json_file='file_log.json')
    logger.info('a')
    logger.debug('should display')
    logger.info('b', {'info': 'b_value'})
    assert std_err.getvalue() == ''
    assert std_out.getvalue() == dedent("""\
        [INFO] [09:33:09 PM - Nov 29, 1973]: a
        [DEBUG] [09:33:09 PM - Nov 29, 1973]: should display
        [INFO] [09:33:09 PM - Nov 29, 1973]: b
               {
                 "info": "b_value"
               }
    """)
    file_log = log_hdl.getvalue()
    lines = [json.loads(line) for line in file_log.splitlines()]
    assert len(lines) == 3
    assert lines[0].get('msg') == 'a'
    assert lines[1].get('msg') == 'should display'
    assert lines[2].get('msg') == 'b'
    assert lines[2].get('context').get('info') == 'b_value'


def test_ci_tool_logger_debug(mocker: MockerFixture) -> None:
    mocker.patch.dict(
        os.environ,
        {'DEBUG_M_LOGS': 'true', **no_color},
        clear=True,
    )
    std_out, std_err, _ = mock_streams(mocker)
    # no need to specify since we are using the environment variable
    logging_config()
    logger.info('a')
    logger.debug('should display')
    logger.info('b', {'info': 'b_value'})
    assert std_err.getvalue() == ''
    assert std_out.getvalue() == dedent("""\
        [INFO] [09:33:09 PM - Nov 29, 1973]: a
        [DEBUG] [09:33:09 PM - Nov 29, 1973]: should display
        [INFO] [09:33:09 PM - Nov 29, 1973]: b
               {
                 "info": "b_value"
               }
    """)


def test_ci_tool_github_plain_str(mocker: MockerFixture) -> None:
    mocker.patch.dict(
        os.environ,
        {'GITHUB_ACTIONS': 'true', **no_color},
        clear=True,
    )
    std_out, std_err, _ = mock_streams(mocker)
    logging_config()
    logger.error('some error')
    logger.warning('some warning')
    logger.info('hello there')
    out = std_out.getvalue()
    assert out == '[INFO] [09:33:09 PM - Nov 29, 1973]: hello there\n'

    err = std_err.getvalue()
    assert err == '::error::some error\n::warning::some warning\n'


def test_ci_tool_tc_plain_str(mocker: MockerFixture) -> None:
    mocker.patch.dict(
        os.environ,
        {'TC': 'true', **no_color},
        clear=True,
    )
    std_out, std_err, _ = mock_streams(mocker)
    logging_config()
    logger.error('some error')
    logger.warning('some warning')
    logger.info('hello there')
    logger.info('', {'context': 'only context'})
    out = std_out.getvalue()
    # technically in this case the context should go one more space
    # but this case is very rare. If I see it more times and it really
    # bothers me i'll fix, for now I can live with it.
    assert out == dedent("""\
        [INFO]: hello there
               {
                 "context": "only context"
               }
    """)

    err = std_err.getvalue()
    assert err == '\n'.join([
        "##teamcity[buildProblem description='some error']",
        "##teamcity[message status='WARNING' text='some warning']",
        '',
    ])

    # Only verifying that there we are in a ci environment to get
    # full coverage for tc.
    tool = get_ci_tool()
    either = tool.env_vars()
    assert not either.is_bad
    assert cast(EnvVars, either.value).ci_env is True


def test_cli_util_error_no_block(mocker: MockerFixture) -> None:
    mocker.patch.dict(
        os.environ,
        {'GITHUB_ACTIONS': 'true', **no_color},
        clear=True,
    )
    std_out, std_err, _ = mock_streams(mocker)
    logging_config()
    logger.error('some error')
    assert std_out.getvalue() == ''
    err = std_err.getvalue()
    assert err == '::error::some error\n'


def test_cli_util_error_block(mocker: MockerFixture) -> None:
    mocker.patch.dict(
        os.environ,
        {'GITHUB_ACTIONS': 'true', **no_color},
        clear=True,
    )
    std_out, std_err, _ = mock_streams(mocker)
    logging_config()
    logger.error('some error', Issue('oops'))
    assert std_out.getvalue() == ''
    err = std_err.getvalue()
    assert err.startswith('::error::some error\n')
    assert '"message": "oops"' in err
