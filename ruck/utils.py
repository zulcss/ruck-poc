import subprocess


def run_command(argv, **kwargs):
    try:
        return subprocess.run(
            argv, **kwargs)
    except subprocess.CalledProcessError as e:
        raise e
