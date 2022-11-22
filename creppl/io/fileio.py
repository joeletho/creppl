# creppl/io/fileio.py

import os
from typing import List

from creppl.io import DEFAULT_FILENAME, DEFAULT_FILE_CONTENTS, WORKING_DIR
from creppl.cmd import Command
from creppl.utils.helpers import file_reset


class FileIO:
    """This class manages the I/O to a specified file. If the file exists, all data will be erased.

        Attributes:
            __line_points: Dictionary(int, int)
                Stores the line number and the index of the line number relative to the file
            __curr_line: int
                The line number of the current line
            filename: str
                The filename of the file to write to and read from.
            filepath: str
                The filepath of the file to write to and read from.
            line_count: int
                The number of '\n' delimited strings in the file
            write_mode: str
                The mode which controls the insertion or replacement of strings into the file.
    """

    def __init__(self, filepath=WORKING_DIR + DEFAULT_FILENAME):
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
        # TODO: check first if the file exists and if the user would like to overwrite
        file_reset(self.filepath, DEFAULT_FILE_CONTENTS)
        self.update()
        self.__curr_line = self.line_count - 2

    def __update_line_points__(self):
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
        self.line_count = len(self.__line_points)

    def __rectify_cursor_bounds__(self):
        _cursor = self.get_cursor()
        if _cursor >= self.get_line_count():
            self.__curr_line = self.get_line_count() - 1
            if self.__curr_line < 1:
                self.__curr_line = 1

    def update(self):
        self.__update_line_points__()
        self.__update_line_count__()
        self.__rectify_cursor_bounds__()

    def set_filename(self, filename: str):
        self.filename = filename
        self.__reset__()

    def set_cursor(self, line_num: int):
        if line_num in range(1, self.line_count):
            self.__curr_line = line_num

    def get_cursor(self):
        return self.__curr_line

    def set_write_mode(self, mode: Command):
        if mode in (Command.INSERT, Command.REPLACE):
            self.write_mode = mode

    def get_write_mode(self):
        return self.write_mode

    def get_current_line(self):
        line = ""
        if self.has_line(self.__curr_line):
            index = self.__line_points[self.__curr_line]
            with open(self.filepath, "r") as file:
                file.seek(index)
                line = file.readline()
        return line[:-1]

    def get_line(self, line_num: int):
        line = ""
        if self.has_line(line_num):
            index = self.__line_points[line_num]
            with open(self.filepath, "r") as file:
                file.seek(index)
                line = file.readline()
        return line[:-1]

    def get_line_count(self):
        return self.line_count

    def write(self, __s: [""], mode: str):
        # "i" is for "insert"
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
        """This erases the last @char found in the file"""

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
        """This deletes the requested line in the file"""
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
        for line in self.__line_points.keys():
            if line == line_num:
                return True
        return False
