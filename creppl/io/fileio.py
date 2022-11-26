# creppl/io/fileio.py

import os
from typing import List

from creppl.io import DEFAULT_FILENAME, DEFAULT_FILE_CONTENTS, WORKING_DIR
from creppl.cmd import Command
from creppl.utils.helpers import file_reset


class FileIO:
    """
    This class manages the I/O to a specified file.

    Attributes
    ----------
    __line_points: Dictionary(int, int)
        Stores the line number and the index of the line number relative to the file
    __curr_line: int
        The line number of the current line
    filename: str
        The filename of the file to write to and read from.
    filepath: str
        The filepath of the file to write to and read from.
    line_count: int
        The number of strings in the file delimited by '\n'
    write_mode: str
        The mode which controls the insertion or replacement of strings into the file.

    Methods
    -------
    __reset__()
    __update_line_points__()
    __update_line_count__()
    __rectify_cursor_bounds__()
    update()
    set_filename(filename: str)
    set_cursor(line_num: int)
    get_cursor() -> int
    set_write_mode(mode: Command)
    get_write_mode() -> Command
    get_current_line() -> str
    get_line(line_num: int)-> str
    get_line_count() -> int
        The number of lines in the file delimited by a '\n'.
    write(__s, mode: str)
        Writes output to the file and calls update().
    erase_last_char(char: str)
        Deletes the last occurrence of the char in the file
    delete_lines(start: int, size: int)
        Deletes line(s) from the file.
    has_line(line_num: int) -> bool
        Compares the number of lines to the line_num parameter.
    """

    def __init__(self, filepath=WORKING_DIR + DEFAULT_FILENAME):
        """
        Parameters
        ----------
        filepath: str
            The path of the output file
        """

        self.__line_points = {}
        self.__curr_line = 0
        self.filename = ""
        self.filepath = filepath
        self.line_count = 0
        self.write_mode = Command.INSERT

        slash = filepath.rfind("/")
        if slash != -1:
            self.filename = filepath[slash + 1:]
        else:
            self.filename = filepath
        self.__reset__()

    def __reset__(self):
        """
        Resets the file to the default contents and updates the class attributes
        """

        file_reset(self.filepath, DEFAULT_FILE_CONTENTS)
        self.update()
        self.__curr_line = self.line_count - 2

    def __update_line_points__(self):
        """
        Updates the line point coordinates of the file

        Coordinates (X,Y) where X is the line number, and Y is the file buffer index to the beginning of the line
        """

        self.__line_points.clear()
        self.__line_points[1] = 0
        line_num = 2
        index = 1
        with open(self.filepath, "r") as file:
            while True:
                char = file.read(1)
                if not char:
                    break
                if char == '\n':
                    self.__line_points[line_num] = index + 1
                    line_num += 1
                index += 1

    def __update_line_count__(self):
        """
        Updates the line counter
        """

        self.line_count = len(self.__line_points)

    def __rectify_cursor_bounds__(self):
        """
        Bounds-checks the cursor position
        """

        _cursor = self.get_cursor()
        if _cursor >= self.get_line_count():
            self.__curr_line = self.get_line_count() - 1
            if self.__curr_line < 1:
                self.__curr_line = 1

    def update(self):
        """
        Updates the line point coordinates, counts, and cursor position of the file
        """

        self.__update_line_points__()
        self.__update_line_count__()
        self.__rectify_cursor_bounds__()

    def set_filename(self, filename: str):
        """
        Sets the filename of the output file.

        Parameters
        ----------
        filename: str
            The filename of the output file
        """

        self.filename = filename
        self.__reset__()

    def set_cursor(self, line_num: int):
        """
        Sets the cursors position to line_num in the file.

        Parameters
        ----------
        line_num: int
            The line number in the file to select
        """

        if line_num in range(1, self.line_count):
            self.__curr_line = line_num

    def get_cursor(self):
        """
        Returns the current line number in the file.

        Returns
        -------
        int
            The current line number in the file

        """

        return self.__curr_line

    def set_write_mode(self, mode: Command):
        """
        Sets the write mode to be used when inserting or replacing lines in the file

        Parameters
        ----------
        mode: Command
            The mode to be used when inserting or replacing lines in the file
        """

        if mode in (Command.INSERT, Command.REPLACE):
            self.write_mode = mode

    def get_write_mode(self):
        """
        Returns the current write mode command

        Returns
        -------
        Command
            The current write mode
        """

        return self.write_mode

    def get_current_line(self):
        """
        Returns the '\n' delimited string in the file of the current line

        Returns
        -------
        str
            A '\n' delimited string
        """

        return self.get_line(self.get_cursor())

    def get_line(self, line_num: int):
        """
        Returns the '\n' delimited string in the file of the line with the number line_num

        Parameters
        ----------
        line_num: int
            The line number of the line to get

        Returns
        -------
        str
            A '\n' delimited string if the line exists, otherwise an empty string
        """

        line = ""
        if self.has_line(line_num):
            index = self.__line_points[line_num]
            with open(self.filepath, "r") as file:
                file.seek(index)
                line = file.readline()
        return line[:-1]

    def get_line_count(self):
        """
        Returns the number of lines in the file delimited by a '\n'.

        Returns
        -------
        int
            The number of lines in the file
        """

        return self.line_count

    def write(self, __s, mode: str):
        """
        Writes output to the file and calls update().

        A custom mode "i" is used to indicate the insertion of the output into the file.

        Parameters
        ----------
        __s: Any
            The data to write to the file
        mode: str
            The mode to use when opening in the file
        """

        if not mode.startswith("i"):
            with open(self.filepath, mode) as file:
                self.__curr_line += 1
                try:
                    file.write(__s)
                except Exception as _ex:
                    print(f'Exception: {_ex}.')
        else:
            def __update_line__(__lines: List[str], __line_index: int, __new_line: str):
                if line_index < len(lines):
                    if self.write_mode == Command.REPLACE:
                        lines[line_index] = __new_line
                    else:
                        lines.insert(line_index, __new_line)
                else:
                    lines.append(__new_line)

            with open(self.filepath, "r+") as file:
                lines = file.readlines()
                line_index = self.__curr_line - 1
                if line_index < len(lines):
                    self.__curr_line += 1
                    for line in __s.splitlines(True):
                        __update_line__(lines, line_index, line)
                        line_index += 1
                else:
                    buf = ""
                    for char in __s:
                        buf += char
                        if char == "\n":
                            lines.append(buf)
                            buf = ""
                    if len(buf) > 0:
                        # There was a line w/o a '\n'
                        lines.append(buf)
                    self.__curr_line = len(lines)

                file.seek(0)
                file.truncate(0)
                try:
                    file.writelines(lines)
                    self.write_mode = Command.INSERT
                except Exception as _ex:
                    print(f'Exception: {_ex}.')
        self.update()

    def erase_last_char(self, char: str):
        """
        Deletes the last occurrence of the char in the file

        Parameters
        ----------
        char: str
            The char to delete
        """

        _cursor = self.get_cursor()
        with open(self.filepath, "r+") as file:
            file.seek(0, os.SEEK_END)
            pos = file.tell() - 1

            while pos > 0 and file.read(1) != char:
                pos -= 1
                file.seek(pos, os.SEEK_SET)

            if pos > 0:
                file.seek(pos, os.SEEK_SET)
                file.truncate()

        self.update()

    def delete_lines(self, start: int, size=1):
        """
        Deletes line(s) from the file.

        Parameters
        ----------
        start: int
            The line number of the first line to delete
        size: int
            The number of lines to delete ascending from the start
        """

        start -= 1
        if 0 <= start:
            with open(self.filepath, "r+") as file:
                lines = file.readlines()
                if start < len(lines):
                    lines = lines[:start] + lines[start + 1 + size:]
                    file.seek(0)
                    file.truncate()
                    file.writelines(lines)
            self.update()

    def has_line(self, line_num: int):
        """
        Compares the line numbers in the file to that of the line_num parameter.

        Parameters
        ----------
        line_num: int
            The line number to search for

        Returns
        -------
        bool
            True if the file contains the line, otherwise False
        """

        for line in self.__line_points.keys():
            if line == line_num:
                return True
        return False
