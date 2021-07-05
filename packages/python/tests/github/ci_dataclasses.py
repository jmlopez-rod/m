from dataclasses import replace as copy
from m.ci.config import ReleaseFrom
from m.github import ci_dataclasses as cid
from ..util import FpTestCase


class CiDataclassesTest(FpTestCase):
    author = cid.Author('login', 'avatarUrl', 'email')
    associated_pr = cid.AssociatedPullRequest(
        author=author,
        merged=False,
        pr_number=1,
        target_branch='',
        target_sha='',
        pr_branch='',
        pr_sha='',
        title='',
        body=''
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
        associated_pr = copy(self.associated_pr)
        commit = copy(self.commit)
        commit.associated_pull_request = None
        # Not in a pr thus empty pr_branch
        self.assertEqual(commit.get_pr_branch(), '')
        # Named pr branch
        commit.associated_pull_request = associated_pr
        associated_pr.pr_branch = 'pr-branch-name'
        self.assertEqual(commit.get_pr_branch(), 'pr-branch-name')

    def test_commit_is_release(self):
        associated_pr = copy(self.associated_pr)
        commit = copy(self.commit)
        commit.associated_pull_request = associated_pr
        # Not a release
        self.assertFalse(commit.is_release(None))
        # Not a release due to branches not matching
        release_from = ReleaseFrom(
            pr_branch='release',
            allowed_files=[],
        )
        associated_pr.pr_branch = 'some-feature'
        self.assertFalse(commit.is_release(release_from))
        # Release
        associated_pr.pr_branch = 'release'
        self.assertTrue(commit.is_release(release_from))

    def test_pr_is_release_pr(self):
        pr = copy(self.pr)
        # Not a release pr
        self.assertFalse(pr.is_release_pr(None))
        # Not a release pr due to branches not matching
        release_from = ReleaseFrom(
            pr_branch='release',
            allowed_files=[],
        )
        pr.pr_branch = 'some-feature'
        self.assertFalse(pr.is_release_pr(release_from))
        # Release PR
        pr.pr_branch = 'release'
        self.assertTrue(pr.is_release_pr(release_from))

    def test_pr_verify_release_pr(self):
        pr = copy(self.pr)
        # Not a release pr
        self.assert_ok(pr.verify_release(None))
        release_from = ReleaseFrom(
            pr_branch='release',
            allowed_files=[],
        )
        pr.pr_branch = 'release'
        # No restrictions
        self.assert_ok(pr.verify_release(release_from))
        # More than allowed
        release_from.allowed_files = ['a', 'b']
        pr.files = ['a', 'b', 'c', 'd']
        pr.file_count = 4
        self.assert_issue(
            pr.verify_release(release_from),
            'max files threshold exceeded in release pr')
        # Not a subset
        release_from.allowed_files = ['a', 'b']
        pr.files = ['a', 'c']
        pr.file_count = 2
        self.assert_issue(
            pr.verify_release(release_from),
            'modified files not subset of the allowed files')
