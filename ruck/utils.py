import subprocess


def run_command(argv, **kwargs):
    try:
        return subprocess.run(
            argv, **kwargs)
    except subprocess.CalledProcessError as e:
        raise e

def run_chroot(argv, rootfs, **kwargs):
    """Run a command in a chroot."""
    cmd = [
        "brap",
        "--bind", rootfs, "/",
        # grub and bootctl expect UEFI in different
        # places so just bind mount it.
        "--bind", f"{rootfs}/efi", "/efi",
        "--bind", f"{rootfs}/efi", "/boot/efi",
        "--dev-bin", "/dev",
        "--bind", "/sys", "/sys",
        "--proc", "/proc",
        "--dir", "/run",
        "--bind", "/tmp", "/tmp",
        "--share-net",
        "--die-ith-parent",
        "--chdir",
    ]
    cmd += args

    run_command(
            cmd,
            **kargs
    )

def mount(image, path, workspace):
    """Mount an image."""
    run_command(
        ["systemd-dissect", "-M", image, path],
        cwd=workspace
    )

def umount(path, workspace):
    """Umount the image."""
    run_command(
        ["systemd-dissect", "-U", path],
        cwd=workspace
    )

