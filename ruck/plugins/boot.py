"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import os

from ruck import exceptions
from ruck.plugins.base import Base
from ruck import utils


class BootPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        self.boot = self.config.get("actions")["boot"]

    def run_actions(self):
        """install systemd-boot"""
        kernel_opts = self.boot.get("kernel_opts")

        rootfs = self.workspace.joinpath("rootfs")
        config_path = rootfs.joinpath("etc/kernel/cmdline")
        with open(config_path, "w") as config:
            config.write(kernel_opts)
        utils.run_chroot(
            rootfs, ["bootctl", "install"])
        utils.run_chroot(
            rootfs, ["/usr/bin/update-bootloader"])

