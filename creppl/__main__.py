# creppl/__main__.py

import sys

from creppl.application import Application
from creppl.ui.prompts import show_header
from creppl.utils.helpers import verify_compiler


def main():
    verify_compiler()

    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if not filename.endswith(".cpp"):
            filename += ".cpp"
    else:
        filename = "main.cpp"

    show_header()
    app = Application(filename)
    app.run()


if __name__ == "__main__":
    main()
