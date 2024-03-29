# Tutorial

This document attempts to describe the process of creating a new project using
the `m` cli to generate a new action. The end result can be seen in
<https://github.com/jmlopez-rod/gha-square-num-m>.

## Create a new project

The `gha-square-num-m` action started with the creation of a devcontainer. You
may skip this if you are comfortable running things locally in your machine. The
only requirement is to have `python>=3.10` and `m` installed.

As of this writing the `m github actions` cli is not yet available in PyPI, so
you need to install directly from the working branch.

```shell
pip install git+https://github.com/jmlopez-rod/m.git@github-actions
```

In this
[commit](https://github.com/jmlopez-rod/gha-square-num-m/commit/5377baa647004cca96b18b6d55132cbd9619412c)
we can see several files being added. The relevant parts are the `Makefile` and
the `src` directory.

### Makefile

Start by adding the `mypy` target. This is to remind developers that we can run
`make mypy`. Please make sure that the `src` directory is included in the
`PYTHONPATH`. This was done via the devcontainer but if you are having issues
with your IDE you may need to add it manually.

```makefile
mypy:
  PYTHONPATH=src mypy src
```

We should also add the `action` target so that we can run `make action`. You are
encouraged to try to run this as many times as possible to make sure the cli is
giving useful information. `make mypy` and `make action` should be the main
commands to run during development.

The final form of the Makefile should be something like this

```makefile
mypy:
	mypy src

action:
	m github actions src/pkg/actions.py

tests:
	./src/tests/run.sh
```

### src directory

Make sure have the following directory structure

```
src
├── pkg
│   ├── __init__.py
│   ├── actions.py
│   ├── inputs.py
│   └── main.py
└── tests
    ├── __init__.py
    ├── run.sh
    └── test_action.py
```

All files can be empty at this point. We'll go over each one of those in the
next section.

## Create the action

We'll start by creating the action inputs. You may define these in the
`actions.py` or in its own file. For this example we have placed them in their
own file since those inputs will be used by the main step.

### inputs.py

```python
# src/pkg/inputs.py
from m.github.actions import InArg, KebabModel


class GithubInputs(KebabModel):
    """Inputs from the Github Action."""

    num: str = InArg(help='the number to square')
```

All inputs and outputs should be defined as strings. The `InArg` is a wrapper
around `pydantic`s `Field` to function to help provide useful descriptions to
the inputs. Note that these description will be used in the final `action.yaml`
file. We can continue adding more inputs as needed, some may even have defaults.
For instance, we could have done

```python
class GithubInputs(kebabModel):
    num: str = InArg(help='description', default='99')
```

Note that in python we use snake case. The `KebabModel` is an extension of
`pydantic.BaseModel` so that it may generate kebab case properties. In the
github actions yaml file we will see all variables using kebab casing.

### main.py

Now we can create the main step. This is the main entry point for the single
action step.

For every step we create we need to define inputs and output models. Since all
the inputs will be coming from the github action we can use the `GithubInputs`
model.

```python
from m.github.actions import KebabModel, OutArg

from pkg.inputs import GithubInputs

class Outputs(KebabModel):
    """Outputs from the Github Action."""

    squared_num: str = OutArg(help='the squared number', export=True)
```

Each step will automatically export all of its outputs, but only some of those
will be exported to the action itself. We may do so my setting `export=True` in
in our output model.

!!! note

    One of the common issues when creating a new action is to forget to add the
    output from a step. There is usually some typo while writing
    `${{ steps.[step-id].outputs.[output-name]}}`. By declaring the outputs with a
    flag now we can forget about it.

Now that the inputs and outputs are defined we can create the main step.

```python
def main(inputs: GithubInputs) -> Res[Outputs]:
    """Square the given number.

    Args:
        inputs: The inputs to the step.

    Returns:
        The outputs of the step or an issue.
    """
    print('Squaring the number')
    num = int(inputs.num)
    result = num * num
    return Good(Outputs(squared_num=str(result)))
```

`Res` and `Good` are imported from `m.core`. Each of the main entries need to
return either a `Good` or `Bad` value. It is ok to raise exceptions to fail the
step as well but `m` has been created using only `OneOf`s in order to avoid
exceptions. The main reason behind this is so that mypy can help us catch errors
by looking at a function signature.

In this particular example we printed some message. This was done intentionally
so that we can test that the action will print it.

Each step may declare a wrapper function to facilitate the creation of the
`actions` object. In this case all we want to import the `main_step` so we
defined

```python
def main_step(
    step_id: str,
    args: GithubInputs
) -> RunStep[GithubInputs, Outputs]:
    """Create a step to square the given number.

    Args:
        step_id: The id of the step.
        inputs: The inputs to the step.

    Returns:
        A step to use in the action.
    """
    return RunStep[GithubInputs, Outputs](id=step_id, run=main, args=args)
```

Note that with this we avoid having to import the `run` function and the outputs
in the final `actions.py` file. This is a personal preference but we can do
whatever we want as long as mypy and your linters allow it. The `RunStep` class
can be imported from `m.github.actions`.

The final step is to run it.

```python
if __name__ == '__main__':
    run_action(main)
```

The `run_action` function will take care of running the action and can be
imported from `m.github.actions`. It makes sure to provide the inputs from the
environment variables and to append the outputs to the file `$GITHUB_OUTPUT`. If
there are any issues while running the `main` function it will display a message
and exit with a non zero code so that Github may fail the run.

### actions.py

It is time to put it all together. The `actions.py` file is the entry point that
we use to generate the `actions.yaml` file.

```python
# src/pkg/actions.py
from m.github.actions import Action

from pkg.inputs import GithubInputs
from pkg.main import main_step

actions = Action(
    name='Square Number',
    description='Square the given number',
    fle_path='action.yaml',
    inputs=GithubInputs,
    steps=[
        main_step(step_id='square', args=GithubInputs(num='inputs.num')),
    ]
)
```

We could have defaulted the value of `file_path` but there can be several
actions in a repo (see [actions/cache]) we need to be explicit about the file
the action is meant to use. To create other actions we could have written

```python
actions = [
  Action(name='action 1', file_path='actions.yaml', ...),
  Action(name='action 2', file_path='another_action/action.yaml', ...),
]
```

At this point we can run `make action` and we should see the `action.yaml` file.
We can also run `make mypy` to make sure that everything is working as expected.
This already should give us confidence that we did not mess up writing the
`action.yaml` file. The only thing that may go wrong is the implementation of
the main function. The next step is write tests to make sure our code works.

## Testing

One of the main pain points for developers is writing tests and setting things
up. A nice thing about writing out actions the way we have done is that it makes
it very easy to test. That is, we can write tests to show what happens with our
functions with different inputs. We can verify that the outputs are written and
are the expected values. We can also verify that that the text written to stdout
and stderr satisfy certain conditions.

The tests have been done in this
[commit](https://github.com/jmlopez-rod/gha-square-num-m/commit/077bab4828c1ef714dc97832667c9a205d055d7e).

One requirement to run the tests is to have `pytest`, `pytest-mock` and
`coverage` installed. `m` has some testing utilities that will make testing
easier.

### test_action.py

One of our goals is to obtain 100% coverage.

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
            name='square_number',
            py_file=f'src/pkg/main.py',
            inputs={'INPUT_NUM': '4'},
            expected_stdout='Squaring the number\n',
            outputs=['squared-num=16'],
        ),
    ],
    ids=lambda tcase: tcase.name,
)
def test_m_gh_actions_api(tcase: TCase, mocker: MockerFixture) -> None:
    run_action_test_case(mocker, tcase)


def test_actions_instance() -> None:
    assert isinstance(actions, Action)
    assert actions.name == 'Square Number'
```

This file has two tests. One tests the `main.py` file and the other tests the
`actions.py` file. The `test_m_gh_actions_api` is a parametrized test that can
run the step with different parameters. In this case we only run with `num`
being `4` We need to provide all inputs with the `INPUT_` prefix. Here we can
see that we are also testing the stdout and the outputs. Try changing any of
those values to make sure that the test fails. The final test is simple to make
sure that the `actions.py` file actually declares the `actions` object. If we
had declared a list we could assert that the object is a list and that it has a
certain length.

!!! tip

    If the step had errors under certain inputs we could also verify that those
    errors are reported. We can do so by adding `errors` to the test case.

    ```
    TCase(
      ...,
      errors=[
        'some text in error',
        'another text',
      ],
    )
    ```

In this way if we ever change the error messages then the tests will fail.

The `run.sh` file is a script that runs the tests. We won't go into details but
this can be used during development by commenting out `SINGLE=false` so that
only certain tests may run.

## CI/CD

This is out of scope for the tutorial but given if `make mypy` and
`make actions` run without issues we can feel assured that the action will work
as expected. What is left in the project is to use `m` to create releases and
start using it.

### Example

In another project we can try out the action.

```yaml
name: example-workflow

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

jobs:
  setup:
    runs-on: ubuntu-22.04
    steps:
      - name: install m
        run: pip install git+https://github.com/jmlopez-rod/m.git@github-actions
      - name: square
        id: square
        uses: jmlopez-rod/gha-square-num@master
        with:
          num: 5
      - name: result
        run: echo "The square of 5 is ${{ steps.square.outputs.num-squared }}"
      - name: square-m
        id: square-m
        uses: jmlopez-rod/gha-square-num-m@master
        with:
          num: 25
      - name: result
        run:
          echo "The square of 25 is ${{ steps.square-m.outputs.squared-num }}"
```

Note that we are using two different actions. One is the first action written in
the [motivation](./intro.md) page and the other one is the one in this tutorial.
The nice thing about this pattern is that the only failure when trying out the
workflow was forgetting to have `m` installed. Other than that the action worked
as expected.

[actions/cache]: https://github.com/actions/cache
