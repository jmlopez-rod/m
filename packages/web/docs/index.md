# Getting started

The goal of `m` is to help maintain Github projects. This usually involves
[keeping a CHANGELOG][changelog], building, publishing and releasing packages.
To achieve this, `m` comes with several utilities that can be used in the Github
pipelines and on the developer's local environment.

This process makes `m` to be opinionated. If the following points are acceptable
by the project's maintainers then `m` may be a nice integration.

## Caveats

### Github repositories

All communication with repositories is done strictly with Github. `git` is used
locally via `ssh` but any other user and pull request information is obtained
via Github's APIs.

!!! warning

    The git configuration should use `ssh` instead of `http`. This is done to avoid
    issues with the developers prefered git tool and/or user interface.

    ```
    [remote "origin"]
      url = git@github.com:<owner>/<repo>.git
    ```

### Changelog

All projects are required to have a `CHANGELOG.md` file that follows the [keep a
changelog][changelog] format. All a developer is required to do is to
write/verify that a changelog entry.

### Versioning

A lot of projects in Github use tags of the form `v1.2.3`. Here we drop the `v`
and simply use the semantic version when creating releases.

### Development flows

`m` currently supports three development flows: `free-flow`,
[`git-flow`][git-flow] and the `m-flow`. Depending on the flow chosen for the
project a few extra setup is required on the Github repository's settings.

[changelog]: https://keepachangelog.com/
[git-flow]: https://nvie.com/posts/a-successful-git-branching-model/
