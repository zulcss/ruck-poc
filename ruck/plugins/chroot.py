"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""
import logging

from ruck import exceptions
from ruck.plugins.base import Base
from ruck import utils


class ChrootPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        self.disk_config = config.get("actions")["disk"]
        self.chroot_config = config.get("actions")["chroot"]
        self.logging = logging.getLogger(__name__)

    def run_actions(self):
        self.logging.info("Running in chroot")
        mounts = self.chroot_config.get("mount")

        if mounts:
            image = self.disk_config.get("image", None)
            self.rootfs = self.workspace.joinpath("rootfs")
            utils.mount(image, self.rootfs, self.workspace)
        
            shell = self.chroot_config.get("shell")

            utils.run_chroot(self.rootfs, shell)

        if mounts:
            utils.umount(self.rootfs, self.workspace)
