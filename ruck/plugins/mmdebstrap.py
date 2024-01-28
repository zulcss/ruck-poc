"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging
import shutil

from ruck.plugins.base import Base
from ruck import exceptions
from ruck import utils


class MmdebstrapPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace

        self.mmdebstrap = shutil.which("mmdebstrap")

    def run_actions(self):
        """Run the mmdebstrap command."""
        if self.mmdebstrap is None:
            raise exceptions.CommandNotFoundError("mmdebstrap is not found.") 

        config = self.config["actions"]["mmdebstrap"]
        suite = config.get("suite", None)
        if suite is None:
            raise exceptions.ConfigError("Suite is not spcecified.")
        target = config.get("target", None)
        if target is None:
            raise exceptions.ConfigError("Target is not specified.")

        # Build the mmdebstrap to build the rootfs
        cmd = [ 
               self.mmdebstrap,
               "--architecture", "amd64",
               "--include", "systemd-sysv",
        ]
        if self.state.debug:
            cmd.extend(["--debug"])
        else:
            cmd.extend(["--verbose"])
        components = config.get("components", None)
        if components:
            cmd.extend([f"--components={','.join(components)}"])
        packages = config.get("packages", None)
        if packages:
            cmd.extend([f"--include={','.join(packages)}"])

        variant = config.get("variant", None)
        if variant:
            cmd.extend([f"--variant={variant}"])
        else:
            # Make the rootfs.tar.gz as small as possible.
            cmd.extend(["--variant", "apt"])

        hooks = config.get("hooks", None)
        if hooks:
            cmd.extend([f"--hook-directory={hook}" for hook in hooks])
        setup_hooks = config.get("setup-hooks", None)
        if setup_hooks:
            cmd.extend([f"--setup-hook={hook}" for hook in setup_hooks])
        extract_hooks = config.get("extract-hook", None)
        if extract_hooks:
            cmd.extend([f"--extract-hook={hook}" for hook in extract_hooks])
        customize_hooks = config.get("customize-hooks", None)
        if customize_hooks:
            cmd.extend([f"--customize-hook={hook}" for hook in
                        customize_hooks]) 
        cmd.extend([suite, target])
        utils.run_command(cmd, cwd=self.workspace)
