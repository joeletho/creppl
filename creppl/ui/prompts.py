# creppl/ui/prompts.py


def show_header():
    print("Creppl - C++ REPL (Read, Evaluate, Print, Loop) written in Python.")
    print("Type \"$help\" for more information.")


def get_input_prompt(curr_line: int):
    prompt = ">>>" + f"[{curr_line}]".center(5) + ": "
    return prompt


def overwrite_prompt(filename: str):
    answer = input(f"File '{filename}' already exists, overwrite? (y/n): ").lower()
    return True if answer.startswith("y") else False


def get_filename_prompt():
    while True:
        filename = input("Enter filename: ").lower()
        if len(filename) == 0:
            print("Filename cannot be empty. ", end="")
        else:
            return filename
