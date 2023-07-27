# [m](https://jmlopez-rod.github.io/m/)

## install

```
pip install jmlopez-m
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

Start by opening the devcontainer in VSCode. Once there open a terminal and run

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
