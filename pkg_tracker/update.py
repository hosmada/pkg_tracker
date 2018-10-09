import sys
from .requirements_updater import RequirementsUpdater


def main(argv=None):
    args = (argv or sys.argv)[:]
    work_branches, base = _parse_args(args)
    RequirementsUpdater(work_branches, base).create_pull()


def _parse_args(args):
    if len(args) == 1:
        return ['master'], 'master'
    elif len(args) == 2:
        return args[1].split(','), 'master'
    elif len(args) >= 2:
        return args[1].split(','), args[2]


if __name__ == "__main__":
    main()
