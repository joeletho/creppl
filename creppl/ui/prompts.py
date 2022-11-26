# creppl/ui/prompts.py


def show_header():
    """
    Prints the Creppl header
    """

    print("Creppl - C++ REPL (Read, Evaluate, Print, Loop) written in Python.")
    print("Type \"$help\" for more information.")


def get_input_prompt(curr_line: int):
    """
    Formats and returns the next input prompt.

    Examples
    --------
    \\  >>> [4] : std::cout << "Hello!";
    \\  Hello!
    \\  >>> [5] :

    Parameters
    ----------
    curr_line: int
        The current line in the file

    Returns
    -------
    str
        The formatted input prompt
    """

    prompt = ">>>" + f"[{curr_line}]".center(5) + ": "
    return prompt


def overwrite_prompt(filename: str):
    """
    Prompt the user for confirmation to overwrite a file

    Parameters
    ----------
    filename:
        The filename of the file

    Returns
    -------
    bool
        True if user enters a string starting with "y", otherwise False
    """
    answer = input(f"File '{filename}' already exists, overwrite? (Y/n): ").lower()
    return True if answer.startswith("y") else False


def get_filename_prompt():
    """
    Prompts and gets user for a filename

    Returns
    -------
    str
        The filename
    """
    while True:
        filename = input("Enter filename: ").lower()
        if len(filename) == 0:
            print("Filename cannot be empty. ", end="")
        else:
            if not filename.endswith(".cpp"):
                filename += ".cpp"

            return filename
