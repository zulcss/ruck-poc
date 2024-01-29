"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""
import pathlib

import click

from ruck.cmd import State

"""global options"""


def debug_option(f):
    def callback(ctxt, param, value):
        state = ctxt.ensure_object(State)
        state.debug = value
        return value
    return click.option(
        "--debug",
        is_flag=True,
        help="Increase verbosity",
        callback=callback
    )(f)


def clean_option(f):
    def callback(ctxt, param, value):
        state = ctxt.ensure_object(State)
        state.clean = value
        return value
    return click.option(
        "--clean",
        is_flag=True,
        help="Cleanup workwpace",
        callback=callback
    )(f)


def config_option(f):
    def callback(ctxt, param, value):
        state = ctxt.ensure_object(State)
        state.config = pathlib.Path(value)
        state.config = state.config.joinpath("config.yaml")

        return value
    return click.option(
        "-C", "--config",
        help="Path to configuration file",
        nargs=1,
        callback=callback
    )(f)


def workspace_option(f):
    def callback(ctxt, param, value):
        state = ctxt.ensure_object(State)
        state.workspace = pathlib.Path(value)
        return value
    return click.option(
        "--workspace",
        help="Path to the ruck workspace",
        nargs=1,
        default="/var/tmp/ruck",
        required=True,
        callback=callback
    )(f)
