"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import os

from ruck.plugins.base import Base
from ruck import utils


class UMountPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        self.mount = config.get("actions")["umount"]

    def run_actions(self):
        rootfs = self.workspace.joinpath("rootfs")
        utils.umount(rootfs, self.workspace)
