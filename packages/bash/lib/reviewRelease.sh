#!/bin/bash

# Adding to path so that npx can work: https://superuser.com/a/39995
pathadd() {
  if [ -d "$1" ] && [[ ":$PATH:" != *":$1:"* ]]; then
    PATH="$1${PATH:+":$PATH"}"
  fi
}
pathadd "${PWD}/node_modules/@PACKAGE_SCOPE/m/bash/lib"

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
echo "**Reviewer Directions:**

 Verify the \`CHANGELOG.md\` file contains a descriptive summary of all the changes in this release.

**PR Author Directions:**

- Wait for reviewers to approve.
- **DO NOT** merge using the merge button.
- run
    \`\`\`sh
    endRelease.sh
    \`\`\`
"
} > m/.m/messages/pr_body.md

# read variables used to create pr
read -r \
  workflow owner repo \
  <<< "$(m jsonq -s ' ' @m/m.json 'workflow' 'owner' 'repo')"


{
  echo "OWNER=$owner"
  echo "REPO=$repo"
  echo "WORKFLOW=$workflow"
  echo "VERSION=$version"
} > m/.m/release.list

if [ "$workflow" == 'm_flow' ]; then
  m github create_pr \
    --owner "$owner" \
    --repo "$repo" \
    --head "$gitBranch" \
    --base master \
    --title "($releaseType) $version" \
    @m/.m/messages/pr_body.md > m/.m/messages/pr_payload.json
  prUrl=$(m jsonq @m/.m/messages/pr_payload.json html_url)
  headSha=$(m jsonq @m/.m/messages/pr_payload.json head.sha)
  prNumber=$(python -c "print('$prUrl'.split('/')[-1])")

  # Add pr number for the endRelease script
  {
    echo "PR=$prNumber"
  } >> m/.m/release.list

  # Display pr url
  {
    set +x
    echo ''
    echo 'Pull request created:'
    echo "  $prUrl"
  }

elif [ "$workflow" == 'git_flow' ]; then
  m github create_pr \
    --owner "$owner" \
    --repo "$repo" \
    --head "$gitBranch" \
    --base master \
    --title "($releaseType) $version" \
    @m/.m/messages/pr_body.md > m/.m/messages/pr_payload.json
  prUrl=$(m jsonq @m/.m/messages/pr_payload.json html_url)
  # Same sha for the next PR - we only need to provide new context for status
  headSha=$(m jsonq @m/.m/messages/pr_payload.json head.sha)
  prNumber=$(python -c "print('$prUrl'.split('/')[-1])")

  {
    echo "Merge only after [$gitBranch]($prUrl) has been merged."
    echo ""
    echo "In case of conflicts, wait until the release has been done and"
    echo "get this branch updated with the new contents of the develop branch."
  } > m/.m/messages/pr_develop_body.md

  prDev=$(m github create_pr \
    --owner "$owner" \
    --repo "$repo" \
    --head "$gitBranch" \
    --base develop \
    --title "($releaseType to develop) $version" \
    @m/.m/messages/pr_develop_body.md | m jsonq html_url)
  prNumberDev=$(python -c "print('$prDev'.split('/')[-1])")

  # Add pr number for the endRelease script
  {
    echo "PR=$prNumber"
    echo "PR_DEV=$prNumberDev"
  } >> m/.m/release.list

  # Display pr urls
  {
    set +x
    echo ''
    echo 'Pull requests created:'
    echo "  ($releaseType): $prUrl"
    echo "  ($releaseType to develop): $prDev"
  }
else
  echo 'unknown workflow'
fi
