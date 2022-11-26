# creppl/io/__init__.py

from creppl.proc import process

"""Global variables to be accessed by the program"""

USER = process.proc_exec('whoami').stdout.read().decode().strip('\n')
WORKING_DIR = f"/home/{USER}/.creppl"
DEFAULT_FILENAME = "main.cpp"
DEFAULT_FILE_CONTENTS = "#include <iostream>\n\nint main() {\n\n}\n"
