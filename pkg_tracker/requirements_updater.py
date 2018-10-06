from datetime import datetime
import os
from github import Github, InputGitTreeElement


CIRCLE_PROJECT_USERNAME = os.environ.get('CIRCLE_PROJECT_USERNAME')
CIRCLE_PROJECT_REPONAME = os.environ.get('CIRCLE_PROJECT_REPONAME')
GITHUB_ACCESS_TOKEN = os.environ.get('GITHUB_ACCESS_TOKEN')
BRANCH_PREFIX = 'requirements-update'
TITLE_PREFIX = 'package update at '


class RequirementsUpdater:
    def __init__(self, work_branches=['master'], base="master"):
        self.work_branches = work_branches
        self.base = base
        self.github_access_token = self._get_github_access_token()
        self.created_at = datetime.utcnow().strftime('%Y%m%d%H%M%S')

    def create_pull(self):
        self._raise_unvalid_env()
        if not self._need_to_commit():
            return
        repo = self._get_repo()
        new_commit = self._commit_requirements_diff(repo)
        branch = self._branch_name()
        repo.create_git_ref(ref='refs/heads/'+branch, sha=new_commit.sha)
        self._create_pull(repo, branch)

    @staticmethod
    def _raise_unvalid_env():
        if not CIRCLE_PROJECT_USERNAME:
            raise Exception("$CIRCLE_PROJECT_USERNAME isn't set")
        if not CIRCLE_PROJECT_REPONAME:
            raise Exception("$CIRCLE_PROJECT_REPONAME isn't set")
        if not GITHUB_ACCESS_TOKEN:
            raise Exception("$GITHUB_ACCESS_TOKEN isn't set")

    def _commit_requirements_diff(self, repo):
        head_ref = repo.get_git_ref(f'heads/{self.base}')
        latest_commit = repo.get_git_commit(head_ref.object.sha)
        base_tree = latest_commit.tree
        os.system('pip install --upgrade -r requirements.txt --user')
        new_packages = os.popen('pip freeze').read()
        new_tree = repo.create_git_tree(
            [InputGitTreeElement(
                path="requirements.txt",
                mode='100644',
                type='blob',
                content=new_packages
            )], base_tree
        )
        return repo.create_git_commit(
            message="commit message",
            parents=[latest_commit],
            tree=new_tree
        )

    def _get_repo(self):
        git = Github(GITHUB_ACCESS_TOKEN)
        repo_name = self._repo_name()
        return git.get_repo(repo_name)

    @staticmethod
    def _repo_name():
        return f'{os.environ["CIRCLE_PROJECT_USERNAME"]}/{os.environ["CIRCLE_PROJECT_REPONAME"]}'

    def _branch_name(self):
        return f'{BRANCH_PREFIX}{self.created_at}'

    @staticmethod
    def _get_github_access_token():
        '''
        TODO: implement for githug enterprise account
        '''
        return GITHUB_ACCESS_TOKEN

    def _create_pull(self, repo, branch):
        title = f'{TITLE_PREFIX}{self.created_at}'
        return repo.create_pull(
            title,
            'body',
            self.base,
            branch,
        )

    def _need_to_commit(self):
        return os.environ.get('CIRCLE_BRANCH') in self.work_branches
