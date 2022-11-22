# creppl/proc/process.py

import subprocess


def proc_exec(cmd_list, shell=False):
    return subprocess.Popen(cmd_list, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
