# creppl/utils/errors.py


def error_invalid_args(statement: str, cmd: tuple):
    """
    Prints an InvalidArgumentError message

    Parameters
    ----------
    statement: str
        The user input statement or invalid arguments
    cmd: Tuple(str, str)
        The command and invalid arguments
    """
    if statement is not None:
        args = statement
    else:
        args = cmd[1]
    n_args = len(args.split())
    print(
        f'InvalidArgumentError: Command \"${cmd[0]}\" takes no arguments, but {n_args} '
        f'{"was" if n_args == 1 else "were"} provided: \"${cmd[0]} {args}\"')
