# m env action

This action ensures that the `m` environment variables are available in a job.

## Documentation

### Inputs

- `m-version`: The version of `m` to use. Defaults to `latest`.
- `ensure-m`: forces the installation of `m` if not available. Defaults to
  `false`.

### Outputs

- `is-release`: Whether the build is meant to be a release.
