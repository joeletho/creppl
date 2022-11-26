# creppl/utils/helpers.py

from creppl.cmd import Command
from creppl.proc.process import proc_exec


def verify_compiler():
    """
    Asserts the user has the correct compiler installed.

    If the assertion fails, a message will be display.
    """

    output = proc_exec("which g++", True).stdout.read().decode().strip()
    assert output == "/usr/bin/g++", "GCC not installed! Install GCC by running \'sudo apt install build-essential\'" \
                                     " and rerun the program."


def has_args(statement: str, kwargs: tuple):
    """
    Returns whether the statement and/or kwargs has arguments

    Parameters
    ---------
    statement:
        The input statement of the user
    kwargs:
        The Command and command arguments

    Returns
    -------
    bool
        True if the statement is not None and kwargs is not None, otherwise False
        or
        True if the statement is not None and kwargs is None, otherwise False
    """

    if len(kwargs) > 1:
        return statement is not None and kwargs[1] is not None
    return statement is not None


def extract_creppl_command(__s):
    """
    Extracts the creppl command in the __s, if present.

    Parameters
    ---------
    __s: str
        The string containing the command

    Returns
    -------
    Tuple(str, None)
        If __s does not contain a command
    Tuple(None, (str , None))
        If __s contains only a command
    Tuple(str, (str, str))
        If __s contains a str, command, and command arguments
    Tuple(str, (str, None))
        If __s contains a str, command, and no command arguments
    """

    from creppl.cmd.on_command import MIN_KWARGS

    __s = __s[1:]

    idx = __s.find(" ", 0)
    if idx == -1:
        if is_creppl_command(__s):
            return None, (__s, None)
        else:
            return __s, None
    if not is_creppl_command(__s[:idx]):
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


def is_creppl_command(cmd: str):
    """
    Returns whether the cmd is a Creppl command.
    Parameters
    ---------
    cmd: str
        The Creppl command to be tested

    Returns
    -------
    bool
        True if the command is a Creppl command, otherwise False
    """

    return cmd in (
        Command.CLS, Command.INSERT, Command.REPLACE, Command.HELP,
        Command.DEL, Command.GOTO, Command.QUIT, Command.PRINT, Command.RESET)


def file_reset(filename: str, __s=""):
    """
    Clears and writes __s to the file

    Parameters
    ---------
    filename: str
        The filename (or path) of the file
    __s: str
        Content to write to the file
    """

    with open(filename, "w+") as file:
        try:
            file.write(__s)
        except Exception as _ex:
            print(f'Exception: {_ex}.')
