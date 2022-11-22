# creppl/io/terminal.py

import sys
import termios
import tty
import traceback
from typing import TextIO


class KeyCode:
    BKSP = 127
    SIGINT = 3
    ENTER = (10, 13)
    PRCHR = range(ord(" "), ord("~") + 1)
    # ANSI Codes
    ESC = ord("\033")
    # C0 Control Code
    CLS = ESC + 12
    # Xterm Sequences
    UP = sum(map(ord, "\033[A"))
    DOWN = sum(map(ord, "\033[B"))
    RIGHT = sum(map(ord, "\033[C"))
    LEFT = sum(map(ord, "\033[D"))
    # VT Sequences
    DEL = sum(map(ord, "\033[3~"))


class Terminal:
    """This class emulates a UNIX terminal which captures user input,
    maintains an input history, and writes output to display.

        Attributes:
            __MAX_HIST_LEN__: int
                The max length of the input history list.
            __stdin: TextIO
                The input stream to acquire.
            __stdout: TextIO
                The output stream to direct output.
            __old_in_fd: TextIO
                The file descriptor of the original input stream.
    """
    __MAX_HIST_LEN__ = 100
    __old_in_fd = TextIO
    __stdin = TextIO
    __stdout = TextIO

    def __init__(self):
        self.__hist_list = [""] * self.__MAX_HIST_LEN__
        self.__put_index = 0
        self.__get_index = -1

    def __acquire__(self, file_descr):
        self.__old_in_fd = termios.tcgetattr(file_descr.fileno())
        tty.setraw(file_descr)
        tty.setcbreak(True)
        self.__stdin = file_descr

    def __print_except___(self):
        # Release IO control and print the exception, then reacquire the IO
        stdin_backup = self.__stdin
        stdout_backup = self.__stdout
        self.release()
        traceback.print_exc()
        self.set_stdin(stdin_backup)
        self.set_stdout(stdout_backup)

    def release(self):
        self.__stdout.write(f"\033[1000D")
        self.__stdout = None
        tty.setcbreak(False)
        termios.tcsetattr(0, termios.TCSAFLUSH, self.__old_in_fd)

    def set_stdin(self, stdin: TextIO):
        self.__acquire__(stdin)

    def set_stdout(self, stdout: TextIO):
        self.__stdout = stdout

    def stdin_read(self, n_char: int):
        return self.__stdin.read(n_char)

    def stdout_write(self, out_str):
        self.__stdout.write(out_str)

    def stdout_flush(self):
        self.__stdout.flush()

    def put(self, in_str):
        try:
            # noinspection PyTypeChecker
            self.__hist_list[self.__put_index] = in_str
            self.__get_index = self.__put_index
            self.__put_index = ((self.__put_index + 1) % self.__MAX_HIST_LEN__)
        except Exception:
            self.__print_except___()

    def prev_hist(self):
        entry = ""
        try:
            if len(self.__hist_list[self.__get_index]) != 0:
                entry = self.__hist_list[self.__get_index]
                self.__get_index = ((self.__get_index - 1) % self.__MAX_HIST_LEN__)
            else:
                entry = self.next_hist()
        except Exception:
            self.__print_except___()
        return entry

    def next_hist(self):
        entry = ""
        try:
            self.__get_index = ((self.__get_index + 1) % self.__MAX_HIST_LEN__)
            if len(self.__hist_list[self.__get_index]) != 0:
                entry = self.__hist_list[self.__get_index]
            else:
                self.__get_index = ((self.__get_index - 1) % self.__MAX_HIST_LEN__)
        except Exception:
            self.__print_except___()
            self.__get_index = ((self.__get_index - 1) % self.__MAX_HIST_LEN__)
        return entry

    def input(self, prompt=""):
        """This function borrows code from Hayoi's Programming Blog:
        http://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html

        This function handles captured input from the Terminal
        """

        # TODO: prompt + selected line
        print(prompt, end="")

        while True:
            self.set_stdin(sys.stdin)
            self.set_stdout(sys.stdout)
            self.stdout_flush()

            input_str = ""
            index = 0
            while True:
                char = ord(self.stdin_read(1))

                if char == KeyCode.SIGINT:
                    self.release()
                    raise KeyboardInterrupt
                elif char in KeyCode.PRCHR:
                    input_str = input_str[:index] + chr(char) + input_str[index:]
                    index += 1
                elif char in KeyCode.ENTER:
                    self.release()
                    print(prompt + input_str)
                    self.put(input_str)
                    yield input_str
                    break
                elif char == KeyCode.BKSP:
                    index = max(1, index)
                    input_str = input_str[:index - 1] + input_str[index:]
                    index -= 1
                elif char != KeyCode.ESC:
                    continue
                else:
                    csi = char + ord(sys.stdin.read(1)) + ord(sys.stdin.read(1))

                    if csi == KeyCode.LEFT:
                        index = max(0, index - 1)
                    elif csi == KeyCode.RIGHT:
                        index = min(len(input_str), index + 1)
                    elif csi == KeyCode.UP:
                        input_str = self.prev_hist()
                        index = len(input_str)
                    elif csi == KeyCode.DOWN:
                        input_str = self.next_hist()
                        index = len(input_str)
                    else:
                        next_char = sys.stdin.read(1)
                        csi = csi + ord(next_char)
                        if csi == KeyCode.DEL:
                            input_str = input_str[:index] + input_str[index + 1:]
                        else:
                            sys.stdin.write(next_char)

                # Print current input-string
                try:
                    # Move all the way left and move to the end of the prompt
                    self.stdout_write(f"\033[1000D")
                    self.stdout_write(f"\033[{str(len(prompt))}C")
                    # Clear to the line
                    self.stdout_write("\033[0K")
                    self.stdout_write(input_str)
                    # Move all the way left again
                    self.stdout_write("\033[1000D")
                    self.stdout_write(f"\033[{str(len(prompt))}C")
                    if index > 0:
                        # Move cursor to index
                        self.stdout_write(f"\033[{index}C")
                    self.stdout_flush()
                except Exception:
                    self.release()
                    traceback.print_exc()
                    break
