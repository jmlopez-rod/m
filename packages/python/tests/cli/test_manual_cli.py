import pytest
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase, assert_streams, run_cli


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd='calc -h',
        expected="""
            usage: calc [-h] <command> ...

            Custom description for the cli.

            options:
              -h, --help  show this help message and exit

            commands:
              <command>   additional help
                calc      repeat of calculator
                calculator
                          provides basic operations
                say_hello
                          say hello
        """,
    ),
    TCase(
        cmd='calc calculator -h',
        expected="""
            usage: calc calculator [-h] <command> ...

            This is a description for the calculator group.

            options:
              -h, --help  show this help message and exit

            commands:
              <command>   additional help
                add       add numbers
                mul       multiply numbers
        """,
    ),
    TCase(
        cmd='calc calculator add 2 3',
        expected="""
            5
        """,
    ),
])
def test_manual_cli_calc(tcase: TCase, mocker: MockerFixture) -> None:
    from tests.cli_samples.calc import main
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker, main)
    assert_streams(std_out, std_err, tcase)


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd='calc -h',
        expected="""
            usage: calc [-h] <command> ...

            Custom description for the cli.

            options:
              -h, --help  show this help message and exit

            commands:
              <command>   additional help
                calc      repeat of calculator
                calculator
                          provides basic operations
                mini      calculator 3
                say_hello
                          say hello
        """,
    ),
    TCase(
        cmd='calc calculator -h',
        expected="""
            usage: calc calculator [-h] <command> ...

            This is a description for the calculator group.

            options:
              -h, --help  show this help message and exit

            commands:
              <command>   additional help
                add       add numbers
                add3      add 3 numbers
        """,
    ),
    TCase(
        cmd='calc calc -h',
        expected="""
            usage: calc calc [-h] <command> ...

            This is a description for the calc group.

            options:
              -h, --help  show this help message and exit

            commands:
              <command>   additional help
                add       add numbers
                add3      add 3 numbers
                mul       multiply numbers
        """,
    ),
    TCase(
        cmd='calc calculator add3 2 3 4',
        expected="""
            9
        """,
    ),
    TCase(
        cmd='calc mini add 2 3 4',
        expected="""
            9
        """,
    ),
])
def test_manual_cli_calc_override(tcase: TCase, mocker: MockerFixture) -> None:
    from tests.cli_samples.calc_override import main
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker, main)
    assert_streams(std_out, std_err, tcase)
