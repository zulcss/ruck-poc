"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import hashlib
import logging
import os
import pathlib
import shutil

from rich.console import Console

from ruck import exceptions
from ruck.ostree import Ostree
from ruck.plugins.base import Base
from ruck.utils import run_command


class OstreePlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        self.console = Console()
        self.logging = logging.getLogger(__name__)
        self.ostree = Ostree(self.state)

    def run_actions(self):
        config = self.config["actions"]["ostree"]
        source = config.get("source", None)
        if source is None:
            raise exceptions.ConfigError(
                "Unable to determine ostree source.")
        repo = config.get("repo", None)
        if repo is None:
            raise exceptions.ConfigError(
                "Unable to determine ostree repo.")
        branch = config.get("branch", None)
        if branch is None:
            raise exceptions.ConfigError(
                "Unable to determine branch.")

        rootfs = f"{self.workspace}/rootfs"
        if os.path.exists(rootfs):
            shutil.rmtree(rootfs)
        os.makedirs(rootfs)

        self.unpack_source(source, rootfs)
        self.setup_boot(rootfs)
        self.convert_to_ostree(rootfs)
        if os.path.exists(repo) is None:
            self.ostree.init(repo)

        self.logging.info(f"Commiting to {repo}. Please wait")
        self.ostree.ostree_commit(
            rootfs,
            branch=branch,
            repo=repo)

    def unpack_source(self, source, rootfs):
        """Unpack the source rootfs.tar.gz and remove directories."""
        self.logging.info(f"Unpacking {source} to {rootfs}.")
        run_command(
            ["tar",
             "-C", rootfs,
             "-xf",
             # ostree complains about /dev/console so exclude the /dev
             # directory from the tarball.
             source,
             "--exclude=./dev/*",
             "--numeric-owner"],
            cwd=self.workspace)

    def setup_boot(self, rootdir):
        """Setup the kernel."""
        rootdir = pathlib.Path(rootdir)
        bootdir = rootdir.joinpath("boot")
        targetdir = rootdir.joinpath("usr/lib/ostree-boot")

        vmlinuz = None
        initrd = None
        dtbs = None
        version = None

        try:
            os.mkdir(targetdir)
        except OSError:
            pass

        for item in os.listdir(bootdir):
            if item.startswith("vmlinuz"):
                assert vmlinuz is None
                vmlinuz = item
                _, version = item.split("-", 1)
            elif item.startswith("initrd.img") or item.startswith("initramfs"):
                assert initrd is None
                initrd = item
            elif item.startswith("dtbs"):
                assert dtbs is None
                dtbs = os.path.join(bootdir, item)
            else:
                # Move all other artifacts as is
                shutil.move(os.path.join(bootdir, item), targetdir)
        assert vmlinuz is not None

        m = hashlib.sha256()
        m.update(open(os.path.join(bootdir, vmlinuz), mode="rb").read())
        if initrd is not None:
            m.update(open(os.path.join(bootdir, initrd), "rb").read())

        csum = m.hexdigest()

        os.rename(os.path.join(bootdir, vmlinuz),
                  os.path.join(targetdir, vmlinuz + "-" + csum))

        if initrd is not None:
            os.rename(os.path.join(bootdir, initrd),
                      os.path.join(targetdir,
                                   initrd.replace(
                                       "initrd.img", "initramfs") + "-" + csum))

    def convert_to_ostree(self, rootdir):
        """Convert rootfs to ostree."""
        rootdir = pathlib.Path(rootdir)
        CRUFT = ["boot/initrd.img", "boot/vmlinuz",
                 "initrd.img", "initrd.img.old",
                 "vmlinuz", "vmlinuz.old"]
        assert rootdir is not None and rootdir != ""

        with self.console.status(f"Converting {rootdir} to ostree."):
            self.sanitize_usr_symlinks(rootdir)

            # Converting /var/lib/dpkg
            os.rename(
                rootdir.joinpath("var/lib/dpkg"),
                rootdir.joinpath("usr/share/dpkg/database"))

            # Converting var
            rootdir.joinpath("usr/share/factory").mkdir(parents=True,
                                                        exist_ok=True)
            os.rename(
                rootdir.joinpath("var"),
                rootdir.joinpath("usr/share/factory/var"))

            # Remove unecessary files
            self.logging.info("Removing unnecessary files.")
            for c in CRUFT:
                try:
                    os.remove(rootdir.joinpath(c))
                except OSError:
                    pass

            # Setup and split out etc
            self.logging.info("Moving /etc to /usr/etc.")
            shutil.move(rootdir.joinpath("etc"),
                        rootdir.joinpath("usr"))

            self.logging.info("Setting up /ostree and /sysroot.")
            try:
                rootdir.joinpath("ostree").mkdir(
                    parents=True, exist_ok=True)
                rootdir.joinpath("sysroot").mkdir(
                    parents=True, exist_ok=True)
            except OSError:
                pass

            self.logging.info("Setting up symlinks.")
            TOPLEVEL_LINKS = {
                "media": "run/media",
                "mnt": "var/mnt",
                "opt": "var/opt",
                "ostree": "sysroot/ostree",
                "root": "var/roothome",
                "srv": "var/srv",
                "usr/local": "../var/usrlocal",
            }
            fd = os.open(rootdir, os.O_DIRECTORY)
            for l, t in TOPLEVEL_LINKS.items():
                shutil.rmtree(rootdir.joinpath(l))
                os.symlink(t, l, dir_fd=fd)

    def sanitize_usr_symlinks(self, rootdir):
        """Replace symlinks from /usr pointing to /var"""
        usrdir = os.path.join(rootdir, "usr")
        for base, dirs, files in os.walk(usrdir):
            for name in files:
                p = os.path.join(base, name)

                if not os.path.islink(p):
                    continue

                # Resolve symlink relative to root
                link = os.readlink(p)
                if os.path.isabs(link):
                    target = os.path.join(rootdir, link[1:])
                else:
                    target = os.path.join(base, link)

                rel = os.path.relpath(target, rootdir)
                # Keep symlinks if they're pointing to a location under /usr
                if os.path.commonpath([target, usrdir]) == usrdir:
                    continue

                toplevel = self.get_toplevel(rel)
                # Sanitize links going into /var, potentially
                # other location can be added later
                if toplevel != 'var':
                    continue

                os.remove(p)
                os.link(target, p)

    def get_toplevel(self, path):
        """Get the top level diretory."""
        head, tail = os.path.split(path)
        while head != '/' and head != '':
            head, tail = os.path.split(head)

        return tail
