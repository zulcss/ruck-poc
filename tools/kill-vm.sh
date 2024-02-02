#!/bin/bash
#
# Copyright (c) 2023 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0

name=$1
if [ -z $name ]; then
   name="ruck-vm"
fi
sudo virsh destroy $name && sudo virsh undefine $name
