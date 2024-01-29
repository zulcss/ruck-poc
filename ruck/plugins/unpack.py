"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""
import logging

from ruck import exceptions
from ruck.plugins.base import Base
from ruck.utils import run_command


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
        self._mount(image, rootfs)
        self._unpack(target, rootfs)
        self._umount(rootfs)

    def _mount(self, image, path):
        """Mount image on the desired path."""
        self.logging.info(f"Mounting {image} on {path}")
        run_command(
            ["systemd-dissect", "-M", image, path],
            cwd=self.workspace
        )

    def _umount(self, path):
        """Umount image."""
        self.logging.info(f"Umounting {path}")
        run_command(
            ["systemd-dissect", "-U", path],
            cwd=self.workspace)

    def _unpack(self, target, rootfs):
        run_command(
            ["tar", "-C", rootfs, "-xf", target, "--numeric-owner"],
            cwd=self.workspace)
