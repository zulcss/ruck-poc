"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging
import os
import shutil

from ruck.plugins.base import Base
from ruck.utils import run_command


class DebosPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        self.logging = logging.getLogger(__name__)

    def run_actions(self):
        config = self.config["actions"]["debos"]
        source = config.get("source")

        ostree_config = config.get("ostree")
        branch = ostree_config.get("branch")
        self.logging.info(f"Found ostree branch: {branch}")
        repo = ostree_config.get("repo")
        self.logging.info(f"Found ostree repository: {repo}")

        ostree_repo = f"{self.workspace}/ostree_repo"
        if os.path.exists(ostree_repo):
            shutil.rmtree(ostree_repo)

        self.logging.info("Creating temporary repository")
        run_command(
            ["ostree", "init", f"--repo={ostree_repo}"],
            cwd=self.workspace)
        self.logging.info(f"Pulling {branch} into temporary repository.")
        run_command(
            ["ostree", "pull-local", f"--repo={ostree_repo}",
             repo, branch],
            cwd=self.workspace)

        self.logging.info("Running debos...")
        run_command(
            ["debos",
             "-t", f"branch:{branch}",
             "-v",
             source], cwd=self.workspace)
