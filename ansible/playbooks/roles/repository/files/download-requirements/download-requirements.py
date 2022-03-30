#!/usr/bin/python3
import datetime
import logging
from os import execv, getuid
from typing import List

import sys

from src.command.toolchain import TOOLCHAINS
from src.config.config import Config
from src.error import DownloadRequirementsError


def install_missing_modules(config: Config):
    """
    Install 3rd party missing modules.
    Used for offline mode.
    """
    tools = TOOLCHAINS[config.os_type.os_family](config.retries)
    config.pyyaml_installed = tools.ensure_pyyaml()

    if config.pyyaml_installed:
        logging.debug(f'Installed {tools.pyyaml_package} package')


def rerun_download_requirements(config: Config):
    """
    Rerun download-requirements after installing missing modules.
    This step is required because python interpreter needs to reload modules.
    Used for offline mode.
    """
    additional_args: List[str] = ['--rerun']

    # carry over info about installed 3rd party modules:
    if config.pyyaml_installed:
        additional_args.append('--pyyaml-installed')

    execv(__file__, sys.argv + additional_args)


def cleanup(config: Config):
    """
    Remove any 3rd party modules.
    Used for offline mode.
    """
    tools = TOOLCHAINS[config.os_type.os_family](config.retries)

    if config.pyyaml_installed:
        logging.info(f'Uninstalling {tools.pyyaml_package} package...')
        tools.uninstall_pyyaml()
        logging.info('Done.')


def main(argv: List[str]) -> int:
    try:
        time_begin = datetime.datetime.now()

        if getuid() != 0:
            print('Error: Needs to be run as root.')
            return 1

        config = Config(argv)

        try:  # make sure that 3rd party modules are installed
            from src.run import run
            run(config)

        except ModuleNotFoundError:
            install_missing_modules(config)
            rerun_download_requirements(config)

        cleanup(config)

        time_end = datetime.datetime.now() - time_begin
        logging.info(f'Total execution time: {str(time_end).split(".")[0]}')
    except DownloadRequirementsError:
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
