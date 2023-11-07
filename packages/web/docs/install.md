# Packaged versions

You can download it from the [Python Package Index][pypi]. For installation of
packages from PyPI, try [pip], it works on all major platforms.

```shell
pip install jmlopez-m
```

To install from a branch run

```shell
pip install git+https://github.com/jmlopez-rod/m.git@[branch-name]
```

or

```
poetry add git+https://github.com/jmlopez-rod/m.git@[branch-name]
```

## Compatibility

Requires `python >= 3.10`.

## `argcomplete`

The `m` cli is made with [argcomplete]. To set it up follow the following
depending on your shell

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

[pypi]: https://pypi.org/project/jmlopez-m/
[pip]: https://pip.pypa.io/en/stable/installation/
[argcomplete]: https://pypi.org/project/argcomplete/
