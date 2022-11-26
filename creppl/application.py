# creppl/application.py

import os

from creppl.io import DEFAULT_FILE_CONTENTS, WORKING_DIR
from creppl.io.terminal import Terminal
from creppl.ui.prompts import get_input_prompt, overwrite_prompt, get_filename_prompt
from creppl.utils.errors import error_invalid_args
from creppl.utils.helpers import *
from creppl.cmd.on_command import *


class Application:
    """
    The class handles the Creppl instance and run loop of the program.

    Attributes
    ----------
    __should_close: bool
        The flag that controls the run loop.
    __bin_dir: str
        The absolute path of the bin directory
    __src_dir: str
        The absolute path of the source directory
    __exec_name: str
        The name of the executable
    __exec_path: str
        The absolute path of the executable
    __filepath: str
        The absolute path of the source file
    __log_filename: str
        The filename of the proc_exec output log (Not common).
    fileio: FileIO
        Handles all file-related writing, reading, and cursor navigation.
    terminal: Terminal
        The terminal that obtains and handles user input
    statement: str
        The input statement the user submits to the program.

    Methods
    -------
    __prepare_filesystem__()
        Creates directories for the working, bin, and src paths, if they do not already exist.
    __validate_filename__(filename: str)
        Sets the filename and prompts the user for permission to overwrite an already-existing file.
    __append_bracket__()
        Deletes the last closing bracket in the file and appends a new closing bracket on the last line of the file.
    __compile_and_execute__()
        Responsible for creating the subprocesses to compile and execute the C++ program and prints any output from
        the subprocess.
    handle_command(statement: str) -> tuple(str, str)
        Called if and only if the input statement by the user starts with the '$' command symbol, this function
        will strip the command from the statement and forward the statement and command to the appropriate
        'on_command' function to be handled.
    commit()
        Finalizes the statement and write by appends an endline to the statement and writes the statement to the
        file at the current cursor position and calls the __append_bracket__() and __compile_and_execute__()
        functions.
    req_quit()
        Prepares the program for quitting by performing a final write, compilation, and execution of the C++
        program and flags the __should_close variable.
    input(prompt="") -> str
        Gets the next input from the user accompanied by an optional prompt.
    run()
        The main loop of the program.
    """

    def __init__(self, filename: str):
        """
        Parameters
        ----------
        filename : str
            The filename to be used for the C++ source and executable.
        """

        self.__should_close = True
        self.__bin_dir = WORKING_DIR + "/bin"
        self.__src_dir = WORKING_DIR + "/src"
        self.__prepare_filesystem__()
        self.__validate_filename__(filename)
        self.__exec_name = filename.strip(".cpp")
        self.__exec_path = self.__bin_dir + "/" + self.__exec_name
        self.__log_filename = "crepl-log.txt"
        self.fileio = FileIO(self.__filepath)
        self.terminal = Terminal()
        self.statement = ""

    def __prepare_filesystem__(self):
        """
        Creates directories for the working, bin, and src paths, if they do not already exist.
        """

        if not os.path.exists(WORKING_DIR):
            os.mkdir(WORKING_DIR)
        if not os.path.exists(self.__bin_dir):
            os.mkdir(self.__bin_dir)
        if not os.path.exists(self.__src_dir):
            os.mkdir(self.__src_dir)

    def __validate_filename__(self, filename: str):
        """
        Sets the filename and prompts the user for permission to overwrite an already-existing file.

        If permission is denied, the user will be asked to input another filename.

        Parameters
        ----------
        filename: str
            The filename to be used for the C++ source and executable.
        """

        while True:
            self.__filepath = self.__src_dir + "/" + filename
            if not os.path.exists(self.__filepath):
                if not filename.endswith(".cpp"):
                    filename += ".cpp"
                break
            else:
                overwrite = overwrite_prompt(filename)
                if overwrite:
                    break
                else:
                    filename = get_filename_prompt()

    def __append_bracket__(self):
        """
        Deletes the last closing bracket in the file and appends a new closing bracket on the last line of the file.

        This is always performed before compiling and executing the C++ program to guarantee that a closing bracket
        exists for main() in the source code for proper execution.
        """

        file_cursor = self.fileio.get_cursor()
        self.fileio.erase_last_char("}")
        closing_bracket = "}\n"
        self.fileio.write(closing_bracket, "a+")
        self.fileio.set_cursor(file_cursor)

    def __compile_and_execute__(self):
        """
        Responsible for creating the subprocesses to compile and execute the C++ program and prints any output from
        the subprocess.

        Any errors or miscellaneous output that occur are written to the output log.
        """

        from datetime import datetime

        # def __set_cpp_version__():
        #     """
        #     -std=c++11
        #     -std=c++14
        #     -std=c++17
        #     -std=c++20
        #     -std=c++23
        #     """
        #     pass

        __STD_CPP__ = 17

        try:
            output = proc_exec(["g++", f"-std=c++{__STD_CPP__}", "-o", self.__exec_path,
                                self.fileio.filepath]).communicate()
        except ChildProcessError as e:
            print(f'ChildProcessError: {e.strerror}.')
            return
        else:
            timestamp = datetime.timestamp(datetime.now())
            datetime = str(datetime.fromtimestamp(timestamp))
            if len(output[1].decode()) > 0:
                err = output[1].decode()
                print(err)
                with open(WORKING_DIR + self.__log_filename, "a+") as file:
                    try:
                        file.write(datetime + " [Error]: " + output[0].decode())
                    except Exception as _ex:
                        print(f'Exception: {_ex}.')
                        return
            else:
                if len(output[0]) > 0:
                    with open(WORKING_DIR + self.__log_filename, "a+") as file:
                        try:
                            file.write(datetime + " [Output]: " + output[0].decode())
                        except Exception as _ex:
                            print(f'Exception: {_ex}.')
                            return

                output = proc_exec(f"/.{self.__exec_path}")
                print(output.stdout.read().decode())

    def handle_command(self, statement: str):
        """
        Called if and only if the input statement by the user starts with the '$' command symbol, this function
        will strip the command from the statement and forward the statement and command to the appropriate
        'on_command' function to be handled.

        If a command is not found or an unknown command is found, the error variable is flagged, a description of the
        error is printed to the console, and the original statement and error flag is returned.

        Any errors that occur while being handled are handled by the appropriate 'on_command' function call and the
        error variable is flagged. Finally, the statement (without command) and the error flag are returned.

        Parameters
        ----------
        statement: str
            The input statement from the user that starts with '$', indicating a command

        Returns
        -------
        Tuple[str, bool]
            statement: str
                The user input statement without the command if found, otherwise is left untouched. If an error
                occurs, 'statement' will be set to None
            error: bool
                True if an error occurred, otherwise False
        """

        statement, kwargs = extract_creppl_command(statement)
        error = False

        if kwargs is None or not is_creppl_command(kwargs[0]):
            error = True
            if statement is None or len(statement) == 0:
                print(
                    f'InvalidArgumentError: Missing command: \"${statement}\".')
            else:
                print(f'SyntaxError: Unknown command: \"${statement}\".')
        else:
            cmd = kwargs[0]

            if cmd == Command.DEL:
                on_command_del(self.fileio, statement, kwargs)
                if not self.fileio.get_line(self.fileio.get_line_count()).__contains__("}"):
                    line_cursor = self.fileio.get_cursor()
                    self.__append_bracket__()
                    self.fileio.set_cursor(line_cursor)
            elif cmd in (Command.INSERT, Command.REPLACE):
                on_command_set_write_mode(self.fileio, cmd, statement, kwargs)
                if statement is None:
                    # It's OK to replace or insert with an empty line
                    statement = ""
            elif cmd == Command.CLS:
                if has_args(statement, kwargs):
                    error_invalid_args(statement, kwargs)
                    statement = None
                else:
                    on_command_cls()
            elif cmd == Command.GOTO:
                on_command_goto(self.fileio, statement, kwargs)
            elif cmd == Command.PRINT:
                if has_args(statement, kwargs):
                    error_invalid_args(statement, kwargs)
                    statement = None
                else:
                    on_command_print(self.fileio)
            elif cmd == Command.RESET:
                if has_args(statement, kwargs):
                    error_invalid_args(statement, kwargs)
                    statement = None
                else:
                    on_command_reset(self.fileio, DEFAULT_FILE_CONTENTS)
            elif cmd == Command.HELP:
                if has_args(statement, kwargs):
                    error_invalid_args(statement, kwargs)
                    statement = None
                else:
                    if on_command_help() is None:
                        self.req_quit()
            elif cmd == Command.QUIT:
                if has_args(statement, kwargs):
                    error_invalid_args(statement, kwargs)
                    statement = None
                else:
                    on_command_quit(self.fileio)
                    self.req_quit()

        return statement, error

    def commit(self):
        """
        Finalizes the statement and write by appends an endline to the statement and writes the statement to the file
        at the current cursor position and calls the __append_bracket__() and __compile_and_execute__() functions.
        """

        self.statement += '\n'
        self.fileio.write(self.statement, "i")
        self.statement = ""

        self.__append_bracket__()
        self.__compile_and_execute__()

    def req_quit(self):
        """
        Prepares the program for quitting by performing a final write, compilation, and execution of the C++ program
        and flags the __should_close variable.
        """

        self.statement = ""
        self.commit()
        print("")
        self.__should_close = True

    def input(self, prompt=""):
        """
        Gets the next input from the user accompanied by an optional prompt.

        If a KeyboardInterrupt exception is caught, req_quit() is called.
        Parameter
        ---------
        prompt: str
            A message to prompt the user for input

        Returns
        -------
        str
            A string containing user input
        """

        try:
            input_str = next(self.terminal.input(prompt))
            return input_str
        except KeyboardInterrupt:
            self.req_quit()

    def run(self):
        """
        The main loop of the program.
        """

        self.__should_close = False
        while not self.__should_close:
            prompt = get_input_prompt(self.fileio.get_cursor())
            self.statement = self.input(prompt)
            if self.__should_close:
                break
            if self.statement.startswith("$"):
                self.statement, error = self.handle_command(self.statement)
                if self.__should_close or self.statement is None or error:
                    continue
            self.commit()
