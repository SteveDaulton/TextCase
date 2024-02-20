"""Helper functions."""

import sys
from pathlib import Path


def get_user_input_or_quit(prompt: str = '') -> str:
    """Return user input or quit.

    Parameters
    ----------
    prompt : str
        The input message prompt.

    Returns
    -------
    str
        The user supplied input. Does not return if input is 'q' or 'Q'.
    """
    user_input = input(f'{prompt}: ')
    if user_input.lower() == 'q':
        sys.exit("Quitting application.")
    return user_input


def input_choice(message: str, *args: str) -> str:
    """Prompt user for choice.

    Keep prompting until a valid choice is selected.
    Uses `get_user_input_or_quit()` to Quit if 'Q' is entered,
    or returns lower-case choice.

    Parameters
    ----------
    message : str
        The message prompt.
    *args : str
        Variable number of valid choices.

    Returns
    -------
    str
        Lower-case user choice.
    """
    choices = [choice.lower() for choice in args]
    print(choices)
    while True:
        user_input = get_user_input_or_quit(message).lower()
        if user_input in str(choices):
            return user_input
        print("Invalid choice.")


def get_user_confirmation(prompt: str = '') -> bool:
    """Prompt user for y/n response.

    Parameters
    ----------
    prompt : str, default=''
        The message prompt.

    Returns
    -------
    bool
        True for 'Y' or False for 'N'.

    Notes
    -----
    Uses `input_choice()` to repeatedly prompt.
    """
    user_input = input_choice(f"{prompt} [Y/N]: ", 'y', 'n')
    return user_input == 'y'


def input_file_prompt() -> Path:
    """Prompt user for file to convert.

    Check that selected file is a readable text file, and
    confirm the intention to convert.

    Returns
    -------
    Path
        The input file path.
    """
    while True:
        user_input = get_user_input_or_quit("Enter file name")
        word_file = Path(user_input)
        full_file_path = word_file.resolve()
        if is_readable_text_file(word_file):
            if get_user_confirmation(f"Update {full_file_path}"):
                return word_file


def is_readable_text_file(file_path: Path) -> bool:
    """Return True if file_path points to a readable text file.

    Parameters
    ----------
    file_path : Path
        The file to be tested.

    Returns
    -------
    bool
        True if assessed to be a plain text file, else False.

    Notes
    -----
    Python tries hard to convert bytes to Unicode, and often uses placeholders
    rather than raising a UnicodeDecodeError, so we will use heuristics to
    estimate the likelihood of the file being a text file.

    We estimate that a large proportion of characters will be in the printable
    ASCII range. If the file has a '.txt' extension, then it is more likely to
    be a text file, so we set the bar lower and allow a greater proportion of
    non-ascii characters.

    This will fail to identify non-Latin text such as Cyrillic or Chinese.
    This simple heuristic approach is adequate for this En language app. For
    more demanding cases, consider using https://pypi.org/project/chardet/ or
    https://pypi.org/project/charset-normalizer/.
    """
    sample_size = 32 * 1024  # Maximum 32 kB read.

    # Printable ASCII characters
    ascii_codes = list(range(0x1F, 0x7F))
    # Add: Tab, LF, CR
    ascii_codes += [0x09, 0x0A, 0x0D]

    # Estimate minimum proportion of single byte characters.
    if file_path.suffix.lower() == '.txt':
        minimum_ascii_proportion = 0.75
    else:
        minimum_ascii_proportion = 0.9
    try:
        with open(file_path, 'rb') as fp:
            # Read a chunk of bytes.
            bin_data = fp.read(sample_size)
            # Number of printable ascii characters
            ascii_count = sum(1 for ch in bin_data if ch in ascii_codes)
            # Convert to string
            str_data = bin_data.decode(encoding='utf-8')
            # Number of utf-8 characters (including non-printable)
            if ascii_count > minimum_ascii_proportion * len(str_data):
                return True
    except (UnicodeDecodeError, FileNotFoundError) as exc:
        print(f'Error. {exc}')
    except IsADirectoryError as exc:
        print(f'Error. {exc}')
    print(f"Invalid file: {file_path}")
    return False
