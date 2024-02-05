"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""
import logging

from ruck.plugins.base import Base
from ruck import utils


class ChrootPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        self.chroot_config = config.get("actions")["chroot"]
        self.logging = logging.getLogger(__name__)

    def run_actions(self):
        self.logging.info("Running in chroot")

        self.rootfs = self.workspace.joinpath("rootfs")

        shell = self.chroot_config.get("shell")
        for cmd in shell:
            utils.run_chroot(self.rootfs, cmd.split())
