#!/bin/bash
set -euxo pipefail

# Branch name should have the version
gitBranch=$(m git branch)
version=$(python -c "print('$gitBranch'.split('/')[1])")
releaseType=$(python -c "print('$gitBranch'.split('/')[0])")

# Add all files to commit
git add .

# Show the status
git status

# Prompt to continue
opt=$(
  set +x;
  1>&2 echo "Do you wish proceed creating the release pull request?"
  read -p "(yes/no)? " ans
  echo $ans
)

# Only proceed with yes
[ "$opt" == 'yes' ] || exit

# Commit the changes
git commit -m "($releaseType) $version" || echo '...'

# Push the changes
 git push -u origin "$gitBranch"

# Create pr body
mkdir -p m/.m/messages
{
  echo "Please review the contents of CHANGELOG.md"
} > m/.m/messages/pr_body.md

# read variables used to create pr
read -r \
  workflow owner repo \
  <<< "$(m jsonq -s ' ' @m/m.json 'workflow' 'owner' 'repo')"


if [ "$workflow" == 'm_flow' ]; then
  m github create_pr \
    --owner "$owner" \
    --repo "$repo" \
    --head "$gitBranch" \
    --base master \
    --title "($releaseType) $version" \
    @m/.m/messages/pr_body.md | m jsonq html_url
elif [ "$workflow" == 'git_flow' ]; then
    prUrl=$(m github create_pr \
      --owner "$owner" \
      --repo "$repo" \
      --head "$gitBranch" \
      --base master \
      --title "($releaseType) $version" \
      @m/.m/messages/pr_body.md | m jsonq html_url)

    {
      echo "Merge only after [$gitBranch]($prUrl) has been merged."
      echo ""
      echo "In case of conflicts, wait until the release has been done and"
      echo "get this branch updated with the new contents of the develop branch."
    } > m/.m/messages/pr_develop_body.md

    m github create_pr \
      --owner "$owner" \
      --repo "$repo" \
      --head "$gitBranch" \
      --base develop \
      --title "($releaseType to develop) $version" \
      @m/.m/messages/pr_develop_body.md | m jsonq html_url
else
  echo 'unknown workflow'
fi
