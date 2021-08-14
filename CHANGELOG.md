# Changelog

The format of this changelog is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).
The project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html)

> Major version zero (0.y.z) is for initial development. Anything may change at any time.
> The public API should not be considered stable.

## [Unreleased]

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

[Unreleased]: https://github.com/jmlopez-rod/m/compare/0.0.3...HEAD
[0.0.3]: https://github.com/jmlopez-rod/m/compare/0.0.2...0.0.3
[0.0.2]: https://github.com/jmlopez-rod/m/compare/0.0.1...0.0.2
[0.0.1]: https://github.com/jmlopez-rod/m/compare/bf286e270e13c75dfed289a3921289092477c058...0.0.1
