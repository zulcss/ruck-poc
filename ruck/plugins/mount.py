"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import os

from ruck import exceptions
from ruck.plugins.base import Base
from ruck import utils


class MountPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        self.mount = config.get("actions")["mount"]

        self.virtuals = [
            ["none", "/proc", ["-t", "proc"]],
            ["/dev", "/dev", ["--bind"]],
            ["none", "/dev/pts", ["-t", "devpts"]],
            ["none", "/dev/shm", ["-t", "tmpfs"]],
            ["none", "/run", ["-t", "tmpfs"]],
            ["none", "/run/lock", ["-t", "tmpfs"]],
            ["none", "/sys", ["-t", "sysfs"]],
            ["/sys/firmware/efi/efivars", "/sys/firmware/efi/efivars/", ["--bind"]],
        ]

    def run_actions(self):
        src = self.mount.get("source", None)
        if src is None:
            exceptions.ConfigError("Source is not specified.")

        rootfs = self.workspace.joinpath("rootfs")
        utils.mount(src, rootfs, self.workspace)

        # Mount the required devices in a chroot.
        for device, mount_point, opts in self.virtuals:
            path = os.path.normpath(os.path.join(rootfs, "./" + mount_point))
            if os.path.ismount(path):
                continue
            if not os.path.exists(path):
                os.mkdir(path)
            utils.run_command(
                ["mount", device, path] + opts
            )
