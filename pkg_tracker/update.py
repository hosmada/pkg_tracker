from .pkg_tracker import RequirementsUpdater


def update(work_branches=['master'], base='master'):
    RequirementsUpdater(work_branches, base).create_pull()