import subprocess


def run_command(argv, **kwargs):
    try:
        return subprocess.run(
            argv, **kwargs)
    except subprocess.CalledProcessError as e:
        raise e


def run_chroot(path, argv, **kwargs):
    """Run a command in a chroot"""
    cmd = ["chroot", str(path)] + argv
    return run_command(cmd, **kwargs)


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
