"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging
import shutil

from rich.console import Console
from stevedore import driver

from ruck.config import Config
from ruck import exceptions
from ruck.log import setup_log


class Runner(object):
    def __init__(self, state):
        self.state = state
        self.logging = logging.getLogger(__name__)
        self.console = Console(highlight=False)
        self.config = Config(self.state)

    def run(self):
        setup_log()

        self.logging.info("Running ruck.")

        self.logging.info("Loading configuration file.")
        if not self.state.config.exists():
            exceptions.ConfigError("Failed to load configuration file.")
        config = self.config.load_config()

        self.logging.info("Settting up workspace")
        name = config.get("name", None)
        if name is None:
            raise exceptions.ConfigError("Workspace name is not specified.")

        self.workspace = self.state.workspace.joinpath(name)
        if self.state.clean:
            self.logging.info("Cleaning up workspace.")
            shutil.rmtree(self.workspace)

        self.logging.info("Copying configuration to workspace")
        shutil.copytree(
            self.state.config.parent,
            self.workspace,
            dirs_exist_ok=True)

        actions = self.config.get_actions(config)
        for action in actions:
            mgr = driver.DriverManager(
                namespace='ruck.plugins',
                name=action,
                invoke_on_load=True,
                invoke_args=(self.state,
                             config,
                             self.workspace),
                )
            mgr.driver.run_actions()
