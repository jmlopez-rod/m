# Motivation

Github actions does not support python as well as it does typescript projects.
The following are thoughts on how to leverage the python type system to help us
create actions with python. To begin we need to be aware of the [metadata
file][gha-metadata].

## `action.yaml`

This file may be placed at the root of the repo. There may be other actions in
the same repo but we'll cover them as we explore.

The first thing to note is that we are expected to create the yaml file of
inputs and outputs and define the composite steps in which we call our python
scripts. Here is a quick example

```yaml
# action.yaml
name: square-number
description: takes in an input number and returns its square
inputs:
  num:
    description: the number to square
    required: true
outputs:
  num-squared:
    description: the input squared
    value: ${{ steps.get-square.outputs.num-squared }}

runs:
  using: 'composite'
  steps:
    - id: get-square
      shell: bash
      env:
        INPUT_NUM: ${{ inputs.num }}
      run: PYTHONPATH="$GITHUB_ACTION_PATH/src" python -m square_number
```

and the python file

```python
# src/square_number.py
import os

def append_to_output(var_name: str, var_value: str) -> None:
    with open(os.environ.get("GITHUB_OUTPUT"), 'a') as f:
        f.write(f'{var_name}={var_value}\n')

def main() -> None:
    num = int(os.environ.get('INPUT_NUM'))
    result = num * num
    append_to_output('num-square', str(result))

if __name__ == '__main__':
    main()
```

One thing to mention here is that the `PYTHONPATH` is set before calling the
main function so that we may be able to use several files in the `src`
directory.

## Downsides

Maintaining the `action.yaml` file is not an easy task. As we add new inputs we
need to also add the input to the step that needs it. Managing outputs is also
not straight forward. We may write to `$GITHUB_OUTPUT` inside a script but we
may forget to declare it in the `action.yaml` file. Just in the creation of the
example above there was 4 mistakes made. Some mistakes were as simple as not
using the proper name of the python module in the `action.yaml` file.

Once we start adding more functionality it gets harder to keep track of the
variables, inputs, outputs and script names and the usual way to test is to
modify the script and use it in a workflow. This is not ideal.

## Prototype

If we can manage to always write the `action.yaml` file by keeping the pattern
of only calling python scripts and providing inputs via environment variables
then we can generate the `action.yaml` and instead create a more strict format
to help us creation actions using python.

The first assumption will be the action can only be executed in an environment
that has `python` and `m`. An attempt can be made by creating a yaml format
where we specify the classes used as inputs and outputs and the function to
execute.

```yaml
# m.yaml prototype
github_actions:
  _python_path: src
  _inputs: square_number.GithubInputs
  square_number:
    - id: square_number
      inputs: square_number.GithubInputs
      outputs: square_number.SquareNumberOutputs
      args:
        num: inputs.num
```

We can verify that the classes exist and provide useful errors instead of
running directly in Github. The downside to this approach is that we are still
bound to make mistakes while creating the configuration. A better approach is to
simply create an `m` cli that takes in the path to a python file with an
`actions` object. This object can be required to be of type `Action` or
`list[Action]`.

Here is an example of how such file could look like

```python
from m.github.actions import Action
from models import GithubInputs
from square_number import MainInputs, main_step


actions = Action(
    file_path='action.yaml',
    name='square-number',
    description='takes in an input number and returns its square',
    inputs=GithubInputs,
    steps=[
        main_step('main', MainInputs(
            main_in='inputs.num',
        )),
    ],
)
```

Every class and function can be inspected to obtain documentation sources and
file locations to help us create the yaml file. Overall, with a pattern like
this the only mistake `mypy` would not be able to help us catch is declaring the
input references from the `inputs` or other steps. But this is a small mistake
which will be caught when generating the metadata `action.yaml` file.

[gha-metadata]:
  https://docs.github.com/en/actions/creating-actions/metadata-syntax-for-github-actions
