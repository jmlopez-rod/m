# m env action

This action ensures that the `m` environment variables are available in a job.

## Documentation

### Inputs

- `m-version`: The version of `m` to use. Defaults to `latest`.
- `ensure-m`: forces the installation of `m` if not available. Defaults to
  `false`.

### Outputs

- `is-release`: Whether the build is meant to be a release.

## Usage

This action will may use [actions/checkout](https://github.com/actions/checkout)
if there is no `m` directory.

### Get `M_TAG`.

```yaml
runs-on: ubuntu-latest
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
steps:
  - name: m env
    uses: jmlopez-rod/m/actions/env@x.y.z # <- Put version in here
  - name: use m env
    run: |
      echo "$M_TAG"
      ls -al
```

In this example `ls -al` will list the contents of the repository showing that
the checkout action was called by the m action.

### Release

Any job that calls `jmlopez-rod/m/actions/env` will have an output called
`is-release`. This can be used to create a release job that only runs when the
value is `'True'`.

```yaml
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      is-release: ${{ steps.m-env.outputs.is-release }}
    steps:
      - name: m env
        id: m-env
        uses: jmlopez-rod/m/actions/env@x.y.z
      # ... more steps like building and testing

  release:
    needs: setup
    if: needs.setup.outputs.is-release == 'True' # <- This is a string, uses Python boolean
    runs-on: ubuntu-latest
    steps:
      # ... release steps
```
