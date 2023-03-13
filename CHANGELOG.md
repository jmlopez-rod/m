# Changelog

The format of this changelog is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).
The project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html)

> Major version zero (0.y.z) is for initial development. Anything may change at any time.
> The public API should not be considered stable.

## [Unreleased]

- Deprecate `endRelease`. Instead we can use `m end_release`.
- When ending a release it switches to the default branch.
- Previously a release could only be finished by the user who started it.
  This can now be done by any user as long as they switch to the release/hotfix
  branch and execute `m end_release`.

## [0.15.2] <a name="0.15.2" href="#0.15.2">-</a> March 04, 2023

- `m start_release` fails when a project has not done any releases.
  Command now does an exception for the case when the latest release is `0.0.0`
  and avoids checking for commits.

## [0.15.1] <a name="0.15.1" href="#0.15.1">-</a> February 25, 2023

- Require pygments >= 2.14.0 and python >= 3.10.

## [0.15.0] <a name="0.15.0" href="#0.15.0">-</a> February 24, 2023

- Deprecate `startRelease` and `startHotfix`. These two bash scripts have been
  rewritten in python. Instead use can use `m start_release` and `m start_hotfix`.
- `m release_setup` has been switched to use a logger.
- `yaml` output has been introduced as well as colors. Currently the only
  way to disable colors is by using the env var `NO_COLOR=true`.
- All cli errors default to `yaml` format.

## [0.14.0] <a name="0.14.0" href="#0.14.0">-</a> February 20, 2023

- Update `m init` to provide information on what it does
- Logger formatter defaults to using colors. May be disabled with `NO_COLOR=true` env var.
- `m.log.colors` provides the `color` function to format any message with color.

## [0.13.0] <a name="0.13.0" href="#0.13.0">-</a> February 18, 2023

- Moved `ciTools` to the `m.log` module. From here on `print` statements
  will be substituted by `logger.info`.
- `run_main` renamed parameters, use `result_handler` and `issue_handler`.
- Introducing environment variables `DEBUG_M_[INSERT_SOMETHING_HERE]`. More on
  that later in the docs. These are meant to make things a bit more verbose in
  a local environment.

## [0.12.2] <a name="0.12.2" href="#0.12.2">-</a> February 09, 2023

- Fix `m ci npm_tag`: Versions with multiple digits not being properly matched.

## [0.12.1] <a name="0.12.1" href="#0.12.1">-</a> February 02, 2023

- skip release to npmjs - previous job did not publish to pypi.

## [0.12.0] <a name="0.12.0" href="#0.12.0">-</a> February 01, 2023

- Using a devcontainer for local development and pipelines.
- 100% python test coverage.

_Breaking Changes_:

- cli utilities no longer use `add_parser`, using `command` and pydantic
  model instead.
- `Issue.data` replaced by `Issue.context`.

## [0.11.2] <a name="0.5.1" href="#0.5.1">-</a> October 13, 2022

- Github graphql changed the order of releases. This hotfix is
  explicit about the order in which we want them to obtain the latest release.

## [0.11.1] <a name="0.11.1" href="#0.11.1">-</a> September 30, 2022

- Revert version prefix. To specify prereleases in npm we need to do
  `>0.0.0-b <0.0.1`. Using version `999.0.0-` would not target pre-releases so
  using `0.0.0` is a shorter string.

## [0.11.0] <a name="0.11.0" href="#0.11.0">-</a> September 30, 2022

- Version prefix for non releases are now `999.0.0-`. This is done so that
  the semver may work when installing pull request builds.
- `fetch_response` has been added so that we may have access to the response
  object as well. This is helpful when we need to inspect response headers.

## [0.10.1] <a name="0.10.1" href="#0.10.1">-</a> September 12, 2022

- Add python 3.7 as a supported version.

## [0.10.0] <a name="0.10.0" href="#0.10.0">-</a> August 01, 2022

- Add `npm` cli command which allows the use of `clean_tag` subcommand.
- Remove deprecated function `call_main`, use `run_main`.

## [0.9.0] <a name="0.9.0" href="#0.9.0">-</a> June 21, 2022

- Add `build_tag_with_version` to `m` configuration: Allows build tags to
  use the current version instead of `0.0.0`.
- Docusaurus have been introduced. There is no docs yet but the static site
  can be accessed at https://jmlopez-rod.github.io/m/

## [0.8.0] <a name="0.8.0" href="#0.8.0">-</a> March 15, 2022

- Make `m` [`mypy` comptabible](https://mypy.readthedocs.io/en/stable/installed_packages.html#creating-pep-561-compatible-packages)
- Linting and tests added.

## [0.7.1] <a name="0.7.1" href="#0.7.1">-</a> March 07, 2022

- Require `typing_extensions` on python installations.

## [0.7.0] <a name="0.7.0" href="#0.7.0">-</a> March 06, 2022

_fixes_: `m ci celt` fails when project has no errors [669bc54](https://github.com/jmlopez-rod/m/commit/669bc5430a2fc8e343082165943e6f8b688eaaf0)

_changes_: Trying not to use `Popen` to make bash calls [6babc6be](https://github.com/jmlopez-rod/m/commit/6babc6bee7bb6ec23e1301456f587e9bab2a688d)

_features_: Publishing to [`npmjs`](https://www.npmjs.com/package/@jmlopez/m) and [`pypi`](https://pypi.org/project/jmlopez-m/). Only releases are published to the public registries. In github we can access the package from
prs and the latest on the `master` branch.

## [0.6.0] <a name="0.6.0" href="#0.6.0">-</a> September 14, 2021

- `m ci celt` has `-i` option to ignore error allowance. This is helpful when
  working on single files or the whole project and we want to see all the errors
  without having to edit the configuration.
- `m ci celt` accepts `-1` as a valid value for the `-m` option. This will
  print all the errors instead of partially showing them.
- `-s` option in `celt` removes error allownances that are set to zero.

## [0.5.0] <a name="0.5.0" href="#0.5.0">-</a> September 11, 2021

- _Breaking Change_: Renamed `m ci lint` to `m ci celt`.
- `celt` cli command adds the following options:
  - `--full-message`: Display the whole error message (useful with pylint)
  - `--file-regex`: When provided it only displays errors of files matching it.
  - `--file-prefix`: A string of the form `[old]:[new]`. It modifies a file
    prefix that matches `old` for `new`. Useful to display file paths when
    running in docker.
  - `--stats-only`: Displays the current number of violations for each rule.

## [0.4.0] <a name="0.4.0" href="#0.4.0">-</a> September 02, 2021

- Add `m github latest_release` to check the latest version of a github repo.
- Fix issues with `startRelease.sh` and `startHotfix.sh` authenticating to
  github by using the `latest_release` command.

## [0.3.1] <a name="0.3.1" href="#0.3.1">-</a> September 02, 2021

- Fix startRelease and startHotfix scripts. When starting a release, the
  script cannot detect the latest version by fetching the tags when using
  the git-flow because the latest tag is in the master branch not develop.

## [0.3.0] <a name="0.3.0" href="#0.3.0">-</a> September 01, 2021

**Breaking Changes**:

- releaseFrom field is no longer used in the m configuration.
- To continue releasing versions we need to specify a "workflow":
  - free_flow: No version, only tags.
  - m_flow: Uses versions but only the master branch is needed.
  - git_flow: Users versions and it uses master and develop branch.
- Removed `releaseSetup.sh`. Instead we should use:
  - `startRelease.sh` and `startHotfix.sh`.

**Features**:

- Add `reviewRelease.sh` to quickly commit the changes and open up a PR.
- Add `endRelease.sh` to merge the PR.

## [0.2.0] <a name="0.2.0" href="#0.2.0">-</a> August 25, 2021

- Add `-m, --max-lines` to `m ci lint` command. It allows us to specify
  the maximum lines that the command should display per error. It
  defaults to 5.
- Fix releaseSetup.sh output. With the deprecation of `call_main` and
  a previous change that was done to it, the releaseSetup and other
  commands display 0 after a successful run.

## [0.1.0] <a name="0.1.0" href="#0.1.0">-</a> August 21, 2021

- Order results from `m ci lint` based on the number of errors found.
- Add command line option to specify branch when creating a github release.

## [0.0.3] <a name="0.0.3" href="#0.0.3">-</a> August 14, 2021

- Issue objects can hide the traceback from displaying
- Add `format_seconds` function.
- Deprecate `call_main`: use `run_main`
- `run_main` allows us to handle the results and issues.
- `m ci lint` supports the output of

  - eslint
  - pycodestyle
  - pylint

  The tool allows us to make the linters continue with the ci process as long
  as we do not introduce any more errors. See more details by checking the
  help options `m ci lint -h`.

## [0.0.2] <a name="0.0.2" href="#0.0.2">-</a> July 28, 2021

- Adds github release command.
- releaseSetup.sh allows creation of release from any branch.
- Fixes issues with http module that may arise when a response is 500.

## [0.0.1] <a name="0.0.1" href="#0.0.1">-</a> July 05, 2021

- Provides basic utilities to create a CI/CD flow via the m cli.
- As a library, it facilities the creation of clis similar to m.

[unreleased]: https://github.com/jmlopez-rod/m/compare/0.15.2...HEAD
[0.15.2]: https://github.com/jmlopez-rod/m/compare/0.15.1...0.15.2
[0.15.1]: https://github.com/jmlopez-rod/m/compare/0.15.0...0.15.1
[0.15.0]: https://github.com/jmlopez-rod/m/compare/0.14.0...0.15.0
[0.14.0]: https://github.com/jmlopez-rod/m/compare/0.13.0...0.14.0
[0.13.0]: https://github.com/jmlopez-rod/m/compare/0.12.2...0.13.0
[0.12.2]: https://github.com/jmlopez-rod/m/compare/0.12.1...0.12.2
[0.12.1]: https://github.com/jmlopez-rod/m/compare/0.12.0...0.12.1
[0.12.0]: https://github.com/jmlopez-rod/m/compare/0.11.2...0.12.0
[0.11.2]: https://github.com/jmlopez-rod/m/compare/0.11.1...0.11.2
[0.11.1]: https://github.com/jmlopez-rod/m/compare/0.11.0...0.11.1
[0.11.0]: https://github.com/jmlopez-rod/m/compare/0.10.1...0.11.0
[0.10.1]: https://github.com/jmlopez-rod/m/compare/0.10.0...0.10.1
[0.10.0]: https://github.com/jmlopez-rod/m/compare/0.9.0...0.10.0
[0.9.0]: https://github.com/jmlopez-rod/m/compare/0.8.0...0.9.0
[0.8.0]: https://github.com/jmlopez-rod/m/compare/0.7.1...0.8.0
[0.7.1]: https://github.com/jmlopez-rod/m/compare/0.7.0...0.7.1
[0.7.0]: https://github.com/jmlopez-rod/m/compare/0.6.0...0.7.0
[0.6.0]: https://github.com/jmlopez-rod/m/compare/0.5.0...0.6.0
[0.5.0]: https://github.com/jmlopez-rod/m/compare/0.4.0...0.5.0
[0.4.0]: https://github.com/jmlopez-rod/m/compare/0.3.1...0.4.0
[0.3.1]: https://github.com/jmlopez-rod/m/compare/0.3.0...0.3.1
[0.3.0]: https://github.com/jmlopez-rod/m/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/jmlopez-rod/m/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/jmlopez-rod/m/compare/0.0.3...0.1.0
[0.0.3]: https://github.com/jmlopez-rod/m/compare/0.0.2...0.0.3
[0.0.2]: https://github.com/jmlopez-rod/m/compare/0.0.1...0.0.2
[0.0.1]: https://github.com/jmlopez-rod/m/compare/bf286e270e13c75dfed289a3921289092477c058...0.0.1
