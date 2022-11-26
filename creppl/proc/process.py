# creppl/proc/process.py

import subprocess


def proc_exec(cmd_list, shell=False):
    """
    A helper function to create a subprocess

    Parameter
    ---------
    cmd_list: Any
        The commands to invoke the subprocess
    shell: bool
        If true, the command will be executed through the shell

    Examples
    --------
    result = proc_exec(["ls","-al", "|", "grep", "python"])
    stdout = result[0]
    stderr = result[1]

    Returns
    -------
    Popen[str]
        The output of the subprocess
    """

    return subprocess.Popen(cmd_list, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
