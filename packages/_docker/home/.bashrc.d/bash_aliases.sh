#!/bin/bash

. "$HOME/.bashrc.d/env.sh"
. "$HOME/.bashrc.d/prompt_command.sh"
. "$HOME/.bashrc.d/user_bashrc.sh"

if [ ! -f "$HOME/.bashrc.d/mdc_bashrc.sh" ]; then
    echo "Please close and open another terminal - mdc_bashrc.sh not found"
else
    . "$HOME/.bashrc.d/mdc_bashrc.sh"
fi
