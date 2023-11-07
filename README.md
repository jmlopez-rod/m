# [m](https://jmlopez-rod.github.io/m/)

## install

```
pip install jmlopez-m
```

To install from a branch run

```
pip install git+https://github.com/jmlopez-rod/m.git@[branch-name]
```

The cli supports `argcomplete`. To set it up follow the following depending on
your shell

```shell
# for fish shell
register-python-argcomplete --shell fish m > /tmp/foo
sudo mv /tmp/foo /usr/share/fish/vendor_functions.d/m.fish

# for bash shell
register-python-argcomplete --shell bash m > /tmp/foo
sudo mv /tmp/foo /usr/share/bash-completion/completions/m

# for zsh
register-python-argcomplete --shell zsh m > /tmp/foo
sudo mv /tmp/foo /usr/share/zsh/site-functions/_m
```

## development

If you are working on a non-intel machine (M1/M2 Macs) you can run
`make buildPy311DevContainer` and update `devcontainer.json` to use the
`m-devcontainer` image.

Open the devcontainer in VSCode. Once there open a terminal and run

```
poetry install
```

and

```
pnpm install
```

to install the dependencies.

There are several make targets to run. The most important one is
`make ci-checks`. Run that since it is the closest to what the CI will run.

Note that part of the documentation relies heavely on the docstrings provided to
the functions, classes and modules in the library. Please run `make devDocs` to
make sure that the documentation is up to date. The documentation site will be
build and deployed to the `gh-pages` branch whenever a new commit is pushed to
the `master` branch.
