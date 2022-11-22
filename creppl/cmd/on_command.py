# creppl/cmd/on_command.py

import sys

from creppl.io.fileio import FileIO
from creppl.ui.prompts import show_header
from creppl.utils.helpers import file_reset

MIN_KWARGS = 2


def on_command_del(fileio: FileIO, statement, kwargs):
    line_num = fileio.get_cursor()
    n_lines = 1
    if kwargs[1] is None or len(kwargs) < MIN_KWARGS or len(kwargs[1]) == 0:
        print("pass")
        pass
    else:
        line_set = kwargs[1].strip(' ').split("-")
        n_args = len(line_set)

        if n_args > MIN_KWARGS:
            print(f'InvalidArgumentError: Command \"{statement}\" cannot contain more than {MIN_KWARGS} arguments.')
            return

        start_arg = line_set[0]
        end_arg = "1"
        if n_args == MIN_KWARGS:
            end_arg = line_set[1]

        if not start_arg.isnumeric() or not end_arg.isnumeric():
            print(
                f'InvalidArgumentError: Unrecognized argument \"{kwargs[1]}\" in statement \"{statement}\". '
                f'Argument for command \"${kwargs[0]}\" must contain a valid integer.')
            return

        # OK, get the number of lines to delete
        start = int(start_arg)
        end = int(end_arg)
        diff = end - start
        n_lines = 1 if diff < 1 else diff
        line_num = start

    fileio.delete_lines(line_num, n_lines)
    fileio.set_cursor(line_num)


def on_command_cls():
    sys.stdout.write("\033[2J\033[1;1H")
    show_header()


def on_command_goto(fileio: FileIO, statement, kwargs):
    if len(kwargs) < MIN_KWARGS or kwargs[1] is None:
        print(f'ValueError: Missing arguments for command \"${kwargs[0]}\".')
        return
    if len(kwargs) > MIN_KWARGS:
        print(f'SyntaxError: Invalid number of arguments in statement \"{statement}\". Command \"${kwargs[0]}\" only '
              f'takes a single argument.')
        return
    if not kwargs[1].isnumeric():
        print(f'InvalidArgumentError: Unrecognized argument \"{kwargs[1]}\" in statement \"{statement}\". Argument '
              f'for command \"${kwargs[0]}\" must contain a valid integer.')
        return

    # TODO if the line is not empty, allow the user to modify
    line_num = int(kwargs[1])
    fileio.set_cursor(line_num)


def on_command_print(fileio: FileIO):
    with open(fileio.filepath, 'r') as file:
        for count, line in enumerate(file):
            print(f"{count + 1}".center(4) + f"| {line}", end="")
        file.close()


def on_command_help():
    from creppl.io.terminal import KeyCode

    __MAX_LINE_LENGTH__ = 80

    def __print_description__(__s, col=0, max_len=__MAX_LINE_LENGTH__):
        __s = __s.split()
        length = 0
        for word in __s:
            word += " "
            word_length = __count_length__(word)
            length += word_length
            if length >= max_len:
                print(f"\n\033[{col}G", end="")
                length = word_length
            print(word, end="")
        print()

    def __count_length__(__s: str):
        """This function will count the length of a string and ignore any ANSI escape sequences"""
        length = 0
        idx = 0
        while idx < len(__s):
            if __s[idx] == chr(KeyCode.ESC):
                idx = __find_first_alpha__(__s, idx + 1)
            else:
                length += 1
            idx += 1
        return length

    def __find_first_alpha__(__s: str, start: int):
        idx = start
        while idx < len(__s):
            if __s[idx].isalpha():
                return idx
            idx += 1

    print("\nWelcome to Creppl's help utility!\n")
    print("\033[1mDESCRIPTION\033[0m\n")
    __print_description__(
        "\033[6GEnter any valid C++ code and view the results instantly, in true REPL fashion. Enhance your "
        "experience by utilizing the available cmd to quickly add, modify, or remove existing code.\n", 6,
        __MAX_LINE_LENGTH__ + 25)
    print()

    __print_description__(
        "\033[6GTo provide a custom name to the resulting .cpp file, pass the name when executing creppl, "
        "such as \"creppl custom-name.cpp\". The .cpp file extension can be omitted and will be added before "
        "compiling the program. Caution: If the file already exists then all data will be erased!\n", 6,
        __MAX_LINE_LENGTH__ + 25)
    print()

    __print_description__(
        "\033[6GAt this time, creppl uses GNU GCC with C++ 17 to compile and execute the program. The ability to "
        "change the compiler and/or standard C++ library may be an added feature in a future release.\n", 6,
        __MAX_LINE_LENGTH__ + 25)
    print()

    print("\033[1mCOMMANDS\033[0m\n")
    cmd_del_title = "\033[6G\033[1m$del\033[0m \033[1m\033[3mn\033[0m|\033[1m\033[3mn-m\033[0m"
    cmd_del_body = "\033[25GDeletes line \033[3mn*\033[0m or deletes lines \033[3mn\033[0m through \033[3mm*\033[0m," \
                   " inclusive. If available, the cursor will be set to line \033[3mn\033[0m. Otherwise, the cursor" \
                   " will be moved to the next available line."
    print(cmd_del_title, end="")
    __print_description__(cmd_del_body, 25)

    # $ins
    cmd_ins_title = "\033[6G\033[1m$ins\033[0m \033[1m\033[3mn\033[0m"
    cmd_ins_body = "\033[25GInsert a string at line \033[3mn\033[0m. If \033[3mn\033[0m is omitted, insertion will " \
                   "be performed at the current line (Default option)."
    print(cmd_ins_title, end="")
    __print_description__(cmd_ins_body, 25)

    # $rep
    cmd_rep_title = "\033[6G\033[1m$rep\033[0m \033[1m\033[3mn\033[0m"
    cmd_rep_body = "\033[25GReplace the string at line \033[3mn\033[0m. If \033[3mn\033[0m is omitted, replacement " \
                   "will be performed on the current line. Note: this option reverts to the default option after " \
                   "writing the string."
    print(cmd_rep_title, end="")
    __print_description__(cmd_rep_body, 25)

    # $goto
    cmd_goto_title = "\033[6G\033[1m$goto\033[0m \033[1m\033[3mn\033[0m\033"
    cmd_goto_body = "[25GMove the cursor to line \033[3mn\033[0m."
    print(cmd_goto_title, end="")
    __print_description__(cmd_goto_body, 25)

    # $cls
    cmd_cls_title = "\033[6G\033[1m$cls\033[0m"
    cmd_cls_body = "\033[25GClears the screen."
    print(cmd_cls_title, end="")
    __print_description__(cmd_cls_body, 25)

    # $print
    cmd_print_title = "\033[6G\033[1m$print\033[0m"
    cmd_print_body = "\033[25GPrint the contents of the file."
    print(cmd_print_title, end="")
    __print_description__(cmd_print_body, 25)

    # $quit
    cmd_quit_title = "\033[6G\033[1m$quit\033[0m"
    cmd_quit_body = "\033[25GQuit the program."
    print(cmd_quit_title, end="")
    __print_description__(cmd_quit_body, 25)
    print("\n\033[2m* [n,m | 0 < n <= m <= number of lines]\033[0m")

    try:
        input("\nhelp>")
        return not None
    except KeyboardInterrupt:
        return None


def on_command_quit(fileio: FileIO):
    with open(fileio.filepath, "a+") as file:
        try:
            file.write("\n}")
        except Exception as _ex:
            print(f'Exception: {_ex}.')


def on_command_set_write_mode(fileio: FileIO, mode, statement, kwargs):
    if kwargs[1] is None or len(kwargs) < MIN_KWARGS or len(kwargs[1]) == 0:
        line_num = fileio.get_cursor()
    elif kwargs[1].isnumeric():
        line_num = int(kwargs[1])
    else:
        print(f'InvalidArgumentError: Unrecognized argument \"{kwargs[1]}\" in statement \"{statement}\". '
              f'Argument for command \"${kwargs[0]}\" must contain a valid integer.')
        return

    fileio.set_cursor(line_num)
    fileio.set_write_mode(mode)


def on_command_reset(fileio: FileIO, __s=""):
    file_reset(fileio.filepath, __s)
    fileio.update()
