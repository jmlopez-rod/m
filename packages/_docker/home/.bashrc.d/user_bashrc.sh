#!/bash/bash

# If not running interactively, don't do anything
[ -z "$PS1" ] && return

# Necessary in this project since we are using live `m`.
export PYTHONPATH="${CONTAINER_WORKSPACE}/packages/python"
export PATH="${CONTAINER_WORKSPACE}/packages/bash/lib:${PATH}"

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

## Colorize the ls output ##
alias ls='ls --color=auto'

## Use a long listing format ##
alias ll='ls -la'

## Show hidden files ##
alias l.='ls -d .* --color=auto'

# enable bash completion in interactive shells
if ! shopt -oq posix; then
 if [ -f /usr/share/bash-completion/bash_completion ]; then
   . /usr/share/bash-completion/bash_completion
 elif [ -f /etc/bash_completion ]; then
   . /etc/bash_completion
 fi
fi
