"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""
import logging
import os
import shutil

from ruck import exceptions
from ruck.plugins.base import Base
from ruck.utils import run_command


class DiskPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config.get("actions")["disk"]
        self.logging = logging.getLogger(__name__)
        self.workspace = workspace

        self.repart = shutil.which("systemd-repart")

    def run_actions(self):
        """Configure the image disk via systemd-repart."""
        self.logging.info("Configuring disk.")
        if self.repart is None:
            raise exceptions.CommandNotFoundError(
                "%s is not found.", self.repart)

        definitions = self.config.get("definitions", None)
        if definitions is None:
            raise exceptions.ConfigError("Partition definitons not found.")
        image = self.config.get("image", None)
        if image is None:
            raise exceptions.ConfigError("Image is not found.")
        size = self.config.get("size", None)
        if size is None:
            raise exceptions.ConfigError("Size is not specified.")

        run_command([
            self.repart,
            "--definitions", definitions,
            "--empty=create",
            "--size", size,
            "--dry-run=no",
            "--discard=no",
            "--offline=true",
            "--no-pager",
            image],
            cwd=self.workspace)
