"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""
import logging

from ruck import exceptions
from ruck import utils
from ruck.plugins.base import Base


class UnpackPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.disk_config = config.get("actions")["disk"]
        self.unpack_config = config.get("actions")["unpack"]
        self.logging = logging.getLogger(__name__)
        self.workspace = workspace

    def run_actions(self):
        self.logging.info("Unpacking tarball.")

        target = self.unpack_config.get("target", None)
        if target is None:
            raise exceptions.ConfigError("Unable to determine tarball.")
        image = self.disk_config.get("image", None)
        if image is None:
            raise exceptions.ConfigError("Unable to determine image.")

        rootfs = self.workspace.joinpath("rootfs")
        utils.mount(image, rootfs, self.workspace)
        self._unpack(target, rootfs)
        utils.umount(rootfs, self.workspace)

    def _unpack(self, target, rootfs):
        utils.run_command(
            ["tar", "-C", rootfs, "-xf", target, "--numeric-owner"],
            cwd=self.workspace)
