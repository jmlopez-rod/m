# m release action

This action calls the Github API to create a release.

## Usage

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
    if: needs.setup.outputs.is-release == 'True'
    runs-on: ubuntu-latest
    steps:
      - name: m env
        uses: jmlopez-rod/m/actions/env@x.y.z
      - name: release
        uses: jmlopez-rod/m/actions/release@x.y.z
```

Other steps in the release job can be added to publish artifacts during a
release. The main parts to have in the release job is the `m env` step and the
`release` step.
