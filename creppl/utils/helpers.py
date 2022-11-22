# creppl/utils/helpers.py

from creppl.cmd import Command
from creppl.proc.process import proc_exec


def verify_compiler():
    output = proc_exec("which g++", True).stdout.read().decode().strip()
    assert output == "/usr/bin/g++", "GCC not installed! Install GCC by running \'sudo apt install build-essential\'" \
                                     " and rerun the program."


def get_space_length(line_num: int):
    return " " * (3 - len(str(line_num)))


def has_args(statement: str, kwargs: tuple):
    if len(kwargs) > 1:
        return statement is not None and kwargs[1] is not None
    return statement is not None


def extract_crepl_command(__s):
    from creppl.cmd.on_command import MIN_KWARGS

    __s = __s[1:]

    idx = __s.find(" ", 0)
    if idx == -1:
        if is_crepl_command(__s):
            return None, (__s, None)
        else:
            return __s, None
    if not is_crepl_command(__s[:idx]):
        return __s, None

    _subs = __s.split(maxsplit=1)
    cmd = _subs[0].lower()

    if len(_subs) >= MIN_KWARGS:
        _subs = _subs[1].split(maxsplit=1)
        _arg = _subs[0]

        has_arg = True
        if not _arg.isnumeric():
            # Check for "n-m" argument
            if len(_arg.split("-", maxsplit=1)) < 2:
                # Not a hyphenated argument
                has_arg = False
        if has_arg:
            if len(_subs) > 1:
                __s = " ".join(_subs[1:])
            else:
                __s = None

            return __s, (cmd, _arg)

    __s = " ".join(_subs)
    return __s, (cmd, None)


def is_crepl_command(cmd: str):
    return cmd in (
        Command.CLS, Command.INSERT, Command.REPLACE, Command.HELP,
        Command.DEL, Command.GOTO, Command.QUIT, Command.PRINT, Command.RESET)


def file_reset(filename: str, __s=""):
    with open(filename, "w+") as file:
        try:
            file.write(__s)
        except Exception as _ex:
            print(f'Exception: {_ex}.')
