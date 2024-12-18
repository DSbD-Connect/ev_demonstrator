import subprocess
import platform


def login(username, password, cheri_on):

    _platform = platform.platform()
    if "arm" not in _platform and "aarch64" not in _platform:  # Debug/dev purposes
        return "1"

    if cheri_on:
        executable = "./auth_cheri.o"
    else:
        executable = "./auth_noncheri.o"

    params = [password, username]

    process = subprocess.Popen([executable] + params,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode("utf-8")
