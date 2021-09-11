x# Changelog

The format of this changelog is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).
The project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html)

> Major version zero (0.y.z) is for initial development. Anything may change at any time.
> The public API should not be considered stable.

## [Unreleased]

## [0.5.0] <a name="0.5.0" href="#0.5.0">-</a> September 11, 2021
- *Breaking Change*: Renamed `m ci lint` to `m ci celt`.
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


[unreleased]: https://github.com/jmlopez-rod/m/compare/0.5.0...HEAD
[0.5.0]: https://github.com/jmlopez-rod/m/compare/0.4.0...0.5.0
[0.4.0]: https://github.com/jmlopez-rod/m/compare/0.3.1...0.4.0
[0.3.1]: https://github.com/jmlopez-rod/m/compare/0.3.0...0.3.1
[0.3.0]: https://github.com/jmlopez-rod/m/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/jmlopez-rod/m/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/jmlopez-rod/m/compare/0.0.3...0.1.0
[0.0.3]: https://github.com/jmlopez-rod/m/compare/0.0.2...0.0.3
[0.0.2]: https://github.com/jmlopez-rod/m/compare/0.0.1...0.0.2
[0.0.1]: https://github.com/jmlopez-rod/m/compare/bf286e270e13c75dfed289a3921289092477c058...0.0.1
