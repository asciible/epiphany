from typing import List

from src.command.command import Command
from src.error import CriticalError


class Yum(Command):
    """
    Interface for `yum`
    """

    def __init__(self, retries: int):
        super().__init__('yum', retries)

    def update(self, enablerepo: str,
                     package: str = None,
                     disablerepo: str = '*',
                     assume_yes: bool = True):
        """
        Interface for `yum update`

        :param enablerepo:
        :param package:
        :param disablerepo:
        :param assume_yes: if set to True, -y flag will be used
        """
        update_parameters: List[str] = ['update']

        update_parameters.append('-y' if assume_yes else '')

        if package is not None:
            update_parameters.append(package)

        update_parameters.append(f'--disablerepo={disablerepo}')
        update_parameters.append(f'--enablerepo={enablerepo}')

        self.run(update_parameters)

    def install(self, package: str,
                assume_yes: bool = True):
        """
        Interface for `yum install -y`

        :param package: packaged to be installed
        :param assume_yes: if set to True, -y flag will be used
        """
        no_ask: str = '-y' if assume_yes else ''
        proc = self.run(['install', no_ask, package], accept_nonzero_returncode=True)

        if proc.returncode != 0:
            if not 'does not update' in proc.stdout:  # trying to reinstall package with url
                raise CriticalError(f'yum install failed for `{package}`, reason `{proc.stdout}`')

    def remove(self, package: str,
               assume_yes: bool = True):
        """
        Interface for `yum remove -y`

        :param package: packaged to be removed
        :param assume_yes: if set to True, -y flag will be used
        """
        no_ask: str = '-y' if assume_yes else ''
        self.run(['remove', no_ask, package])

    def is_repo_enabled(self, repo: str) -> bool:
        output = self.run(['-y',
                           'repolist',
                           'enabled']).stdout
        if repo in output:
            return True

        return False

    def find_rhel_repo_id(self, patterns: List[str]) -> List[str]:
        output = self.run(['-y',
                           'repolist',
                           'all']).stdout

        repos: List[str] = []
        for line in output.split('\n'):
            for pattern in patterns:
                if pattern in line:
                    repos.append(pattern)

        return repos

    def accept_keys(self):
        # to accept import of repo's GPG key (for repo_gpgcheck=1)
        self.run(['-y', 'repolist'])

    def is_repo_available(self, repo: str) -> bool:
        retval = self.run(['-q',
                           '--disablerepo=*',
                           f'--enablerepo={repo}',
                           'repoinfo']).returncode

        if retval == 0:
            return True

        return False

    def makecache(self, fast: bool = True,
                  assume_yes: bool = True):
        args: List[str] = ['makecache']

        args.append('-y' if assume_yes else '')

        if fast:
            args.append('fast')

        self.run(args)

    def list_all_repo_info(self) -> List[str]:
        args: List[str] = ['-y',
                           'repolist',
                           '-v',
                           'all']
        return self._run_and_filter(args)
