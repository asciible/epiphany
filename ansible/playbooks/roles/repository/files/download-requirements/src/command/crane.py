from os import chmod
from pathlib import Path
from shutil import move
from tempfile import mkstemp
from typing import List

from src.command.command import Command


class Crane(Command):
    """
    Interface for Crane
    """

    def __init__(self, retries: int):
        super().__init__('crane', retries)

    def pull(self, image_name: str,
             destination: Path,
             platform: str,
             legacy_format: bool = True,
             insecure: bool = True):
        """
        Download target image file

        :param image_name: address to the image
        :param destination: where to store the downloaded image
        :param platform: for which platform file will be downloaded
        :param legacy_format: use legacy format
        :param insecure: allow image references to be fetched without TLS
        """
        crane_params: List[str] = ['pull']

        if insecure:
            crane_params.append('--insecure')

        crane_params.append(f'--platform={platform}')

        if legacy_format:
            crane_params.append('--format=legacy')

        crane_params.append(image_name)

        tmpfile = mkstemp()

        crane_params.append(tmpfile[1])

        self.run(crane_params)

        chmod(tmpfile[1], 0o0644)

        move(tmpfile[1], str(destination))
