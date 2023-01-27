from m.cli import run_main
from m.core import Bad, Good, Issue, issue
from pytest_mock import MockerFixture


def failure_func():
    raise RuntimeError('failure')


def handlers(mocker: MockerFixture):
    return mocker.stub(), mocker.stub()


def test_run_main_success(mocker: MockerFixture):
    on_success, on_failure = handlers(mocker)
    exit_code = run_main(lambda:  Good('some output'), on_success, on_failure)
    assert exit_code == 0
    on_success.assert_called_once_with('some output')
    on_failure.assert_not_called()


def test_run_main_unknown_error(mocker: MockerFixture):
    on_success, on_failure = handlers(mocker)
    exit_code = run_main(failure_func, on_success, on_failure)
    assert exit_code == 1

    # https://stackoverflow.com/a/39669722
    args, _ = on_failure.call_args_list[0]
    assert isinstance(args[0], Issue)
    assert args[0].message == 'unknown caught exception'
    on_success.assert_not_called()


def test_run_main_non_issue(mocker: MockerFixture):
    on_success, on_failure = handlers(mocker)
    exit_code = run_main(lambda: Bad('oops'), on_success, on_failure)
    assert exit_code == 1

    args, _ = on_failure.call_args_list[0]
    assert isinstance(args[0], Issue)
    assert args[0].message == 'non-issue exception'
    on_success.assert_not_called()


def test_run_main_issue(mocker: MockerFixture):
    on_success, on_failure = handlers(mocker)
    exit_code = run_main(lambda: issue('oops'), on_success, on_failure)
    assert exit_code == 1

    args, _ = on_failure.call_args_list[0]
    assert isinstance(args[0], Issue)
    assert args[0].message == 'oops'
    on_success.assert_not_called()
