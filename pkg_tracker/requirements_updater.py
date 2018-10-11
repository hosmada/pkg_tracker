from datetime import datetime
import os
import re
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
        old_packages, new_packages = self._get_old_and_new_packages()
        new_commit = self._commit_requirements_diff(repo, new_packages)
        branch = self._branch_name()
        repo.create_git_ref(ref='refs/heads/'+branch, sha=new_commit.sha)
        self._create_pull(repo, branch, old_packages, new_packages)

    @staticmethod
    def _raise_unvalid_env():
        if not CIRCLE_PROJECT_USERNAME:
            raise Exception("$CIRCLE_PROJECT_USERNAME isn't set")
        if not CIRCLE_PROJECT_REPONAME:
            raise Exception("$CIRCLE_PROJECT_REPONAME isn't set")
        if not GITHUB_ACCESS_TOKEN:
            raise Exception("$GITHUB_ACCESS_TOKEN isn't set")

    def _commit_requirements_diff(self, repo, new_packages):
        head_ref = repo.get_git_ref(f'heads/{self.base}')
        latest_commit = repo.get_git_commit(head_ref.object.sha)
        base_tree = latest_commit.tree
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

    def _get_old_and_new_packages(self):
        old_packages = os.popen('cat requirements.txt').read()
        os.system('pip install --upgrade --no-cache-dir -r requirements.txt')
        new_packages = self._pure_new_packages(
            old_packages, os.popen('pip freeze').read()
        )
        return old_packages, new_packages

    def _pure_new_packages(self, old_packages, new_packages):
        old_pkg_list = self._packages_to_list(old_packages)
        new_pkg_list = self._packages_to_list(new_packages)
        diff_pkg_list = list(set(new_pkg_list) - set(old_pkg_list))
        return '\n'.join(
            [pkg_row for pkg_row in new_pkg_list if self._pkg_name(pkg_row) 
                not in diff_pkg_list]
        )

    def _get_repo(self):
        git = Github(GITHUB_ACCESS_TOKEN)
        repo_name = self._repo_name()
        return git.get_repo(repo_name)

    @staticmethod
    def _repo_name():
        return f'{CIRCLE_PROJECT_USERNAME}/{CIRCLE_PROJECT_REPONAME}'

    def _branch_name(self):
        return f'{BRANCH_PREFIX}{self.created_at}'

    @staticmethod
    def _get_github_access_token():
        '''
        TODO: implement for githug enterprise account
        '''
        return GITHUB_ACCESS_TOKEN

    def _create_pull(self, repo, branch, old_packages, new_packages):
        title = f'{TITLE_PREFIX}{self.created_at}'
        body = self._generate_pull_body(old_packages, new_packages)
        return repo.create_pull(
            title,
            body,
            self.base,
            branch,
        )

    def _need_to_commit(self):
        return os.environ.get('CIRCLE_BRANCH') in self.work_branches

    def _generate_pull_body(self, old_packages, new_packages):
        pkg_diff_list = list()
        for old_pkg, new_pkg in zip(
            self._packages_to_list(old_packages),
            self._packages_to_list(new_packages)
        ):
            if old_pkg == new_pkg:
                continue
            pkg_name = self._pkg_name(new_pkg)
            old_version = old_pkg.lstrip(f"{pkg_name}==")
            new_version = new_pkg.lstrip(f"{pkg_name}==")
            row = f'- [ ] {pkg_name} {old_version} -> {new_version}'
            pkg_diff_list.append(row)
        return '\n'.join(pkg_diff_list)

    @staticmethod
    def _packages_to_list(packages):
        return packages.split('\n')

    @staticmethod
    def _pkg_name(pkg_row):
        return re.sub(r'=.*', '', pkg_row)
