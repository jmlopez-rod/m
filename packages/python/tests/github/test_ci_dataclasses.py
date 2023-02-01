from m.github import ci_dataclasses as cid

from ..util import FpTestCase


class CiDataclassesTest(FpTestCase):
    author = cid.Author(login='login', avatar_url='avatarUrl', email='email')
    associated_pr = cid.AssociatedPullRequest(
        author=author,
        merged=False,
        pr_number=1,
        target_branch='',
        target_sha='',
        pr_branch='',
        pr_sha='',
        title='',
        body='',
    )
    commit = cid.Commit(
        author_login='',
        short_sha='',
        sha='',
        message='',
        url='',
        associated_pull_request=associated_pr,
    )
    pr = cid.PullRequest(
        author=author,
        pr_number=1,
        pr_branch='',
        target_branch='',
        target_sha='',
        url='',
        title='',
        body='',
        file_count=2,
        files=[],
        is_draft=False,
    )

    def test_commit_get_pr_branch(self):
        associated_pr = self.associated_pr.copy()
        commit = self.commit.copy()
        commit.associated_pull_request = None
        # Not in a pr thus empty pr_branch
        self.assertEqual(commit.get_pr_branch(), '')
        # Named pr branch
        commit.associated_pull_request = associated_pr
        associated_pr.pr_branch = 'pr-branch-name'
        self.assertEqual(commit.get_pr_branch(), 'pr-branch-name')

    def test_commit_is_release(self):
        associated_pr = self.associated_pr.copy()
        commit = self.commit.copy()
        commit.associated_pull_request = associated_pr
        # Not a release
        self.assertFalse(commit.is_release(None))
        # Not a release due to branches not matching
        release_prefix = 'release'
        associated_pr.pr_branch = 'some-feature'
        self.assertFalse(commit.is_release(release_prefix))
        # Release
        associated_pr.pr_branch = 'release'
        self.assertTrue(commit.is_release(release_prefix))

    def test_pr_is_release_pr(self):
        pr = self.pr.copy()
        # Not a release pr
        self.assertFalse(pr.is_release_pr(None))
        # Not a release pr due to branches not matching
        release_prefix = 'release'
        pr.pr_branch = 'some-feature'
        self.assertFalse(pr.is_release_pr(release_prefix))
        # Release PR
        pr.pr_branch = 'release'
        self.assertTrue(pr.is_release_pr(release_prefix))
