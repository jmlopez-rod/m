#!/bin/bash
# This file overrides the default prompt command. It displays the
# current git branch and status in the prompt.

RESET=$(tput sgr0)
WHITE=$(tput setaf 255)
GRAY=$(tput setaf 239)
ORANGE=$(tput setaf 172)
BLUE=$(tput setaf 4)

# https://stackoverflow.com/a/16296466
PROMPT_COMMAND="${PROMPT_COMMAND}${PROMPT_COMMAND:+;} prompter"

function prompter() {
  local end="\[$WHITE\]\$ \[$RESET\]"
  if [[ -n $(git branch 2> /dev/null) ]]; then
    prompt="$(_git_prompter)"
    export PS1="$prompt$end"
  else
    export PS1="\[$ORANGE\]\w$end"
  fi
}

function _git_prompter() {
  local arrow='\342\236\234'
  local branch
  local git_status
  local colors
  local statuses
  local statusKey
  local statusIndex
  local statusColor
  local status
  local repoPath
  local repo
  local relPath
  local blue
  local gray
  branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
  [[ "$branch" == 'HEAD' ]] && branch=$(git rev-parse --short HEAD 2>/dev/null)
  git_status="$(git status 2> /dev/null)"
  hash_index() {
    case $1 in
      'unknown') echo 0;;
      'untracked') echo 1;;
      'stash') echo 2;;
      'clean') echo 3;;
      'ahead') echo 4;;
      'behind') echo 5;;
      'staged') echo 6;;
      'dirty') echo 7;;
      'diverged') echo 8;;
    esac
  }
  # See for more colors: https://unix.stackexchange.com/a/438357
  colors=(
      '\[\033[38;5;20m\]'   # unknown: dark blue
      '\[\033[38;5;76m\]'   # untracked: mid lime-green
      '\[\033[38;5;76m\]'   # stash: mid lime-green
      '\[\033[38;5;82m\]'   # clean: brighter green
      '\[\033[38;5;226m\]'  # ahead: bright yellow
      '\[\033[38;5;142m\]'  # behind: darker yellow-orange
      '\[\033[38;5;214m\]'  # staged: orangey yellow
      '\[\033[38;5;202m\]'  # dirty: orange
      '\[\033[38;5;196m\]'  # diverged: red
  );
  statuses=(
    '(Wat?)'  # unknown
    '?'      # untracked
    '+'      # stash
    ''       # clean
    '>'      # ahead
    '<'      # behind
    '^'      # staged
    '*'      # dirty
    '!'      # diverged
  );
  statusKey="$(_get_git_status_key "$git_status")"
  statusIndex="$(hash_index "$statusKey")"
  statusColor="${colors[$statusIndex]}"
  status="${statuses[$statusIndex]}"
  repoPath=$(git rev-parse --show-toplevel)
  repo="$(basename "$repoPath")"
  relPath="${PWD/$repoPath/^}"
  blue="\[$BLUE\]"
  gray="\[$GRAY\]"

  dkInfo="devcontainer"

  echo "$statusColor$arrow $green$dkInfo$white:$blue$repo ${gray}[$statusColor$branch$status$gray] $gray$relPath"
}

function _get_git_status_key() {
  local git_status=$1
  if [[ $git_status =~ 'Untracked files' ]]; then
    echo 'untracked'
  elif git stash show &>/dev/null; then
    echo 'stash'
  elif [[ $git_status =~ 'Your branch is ahead' ]]; then
    echo 'ahead'
  elif [[ $git_status =~ 'Your branch is behind' ]]; then
    echo 'behind'
  elif [[ $git_status =~ 'working tree clean' ]]; then
    echo 'clean'
  elif [[ $git_status =~ 'Changes to be committed' ]]; then
    echo 'staged'
  elif [[
    $git_status =~ 'Changed but not updated' ||
    $git_status =~ 'Changes not staged'      ||
    $git_status =~ 'Unmerged paths'
  ]]; then
    echo 'dirty'
  elif [[ $git_status =~ 'Your branch'.+diverged ]]; then
    echo 'diverged'
  fi
}
