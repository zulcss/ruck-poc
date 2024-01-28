"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import click

from ruck.cmd.options import clean_option
from ruck.cmd.options import config_option
from ruck.cmd.options import debug_option
from ruck.cmd.options import workspace_option
from ruck.cmd import pass_state_context
from ruck.runner import Runner


@click.command
@pass_state_context
@debug_option
@config_option
@clean_option
@workspace_option
def cli(state, debug, config, clean, workspace):
    Runner(state).run()


def main():
    cli(prog_name="ruck")
