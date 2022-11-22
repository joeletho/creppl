# creppl/cmd/__init__.py

import enum


class Command(enum.auto):
    """CREPPL Terminal Commands"""
    DEL = "del"
    GOTO = "goto"
    HELP = "help"
    CLS = "cls"
    INSERT = "ins"
    PRINT = "print"
    QUIT = "quit"
    REPLACE = "rep"
    RESET = "reset"
