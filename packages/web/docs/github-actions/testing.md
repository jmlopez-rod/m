# Testing

`m` provides several utilities to help us test our actions. We can start with
this example

```python
import pytest
from m.github.actions import Action
from m.testing import ActionStepTestCase as TCase
from m.testing import run_action_test_case
from pytest_mock import MockerFixture

from pkg.actions import actions


@pytest.mark.parametrize(
    'tcase',
    [
        TCase(
            name='test_id',
            py_file=f'src/pkg/main.py',
            inputs={
              'INPUT_ARG_A': 'val_a',
              'INPUT_ARG_B': 'val_b',
            },
            expected_stdout='Anything we print to stdout',
            outputs=['some-output=some_value'],
        ),
    ],
    ids=lambda tcase: tcase.name,
)
def test_m_gh_actions_api(tcase: TCase, mocker: MockerFixture) -> None:
    run_action_test_case(mocker, tcase)


def test_actions_instance() -> None:
    assert isinstance(actions, Action)
    assert actions.name == 'Action Name'
```

!!! important

    This is not required but it is recommended to have this in the `__init__.py` for
    the root of the tests.

    ```python
    from m.testing import block_m_side_effects, block_network_access

    block_m_side_effects()
    block_network_access()
    ```

    This will make sure that our tests do not make any calls to the internet and
    prevents our code from writing files. Instead it will force us to create mocks.

## Testing API

<!-- prettier-ignore -->
::: m.testing
    options:
        heading_level: 3
        show_root_toc_entry: false
        show_root_full_path: false
