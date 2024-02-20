"""Converts a text file to lower case.

Uses temporary file to allow processing files larger than RAM.
"""

# import argparse
import shutil
import tempfile
from pathlib import Path

from helpers import (input_file_prompt, input_choice)


def convert_case(filename: Path, char_case: str) -> None:
    """Convert filename to upper or lower-case.

    Parameters
    ----------
    filename : Path
        Path to text file to be converted.

    char_case : str
        'u' => Uppercase
        'l' => Lowercase
        't' => Title  case
        's' => Sentence case
    """
    try:
        assert char_case in 'ults'
    except AssertionError:
        print("Error. Unsupported char_case option.")
        return

    methods = {'u': str.upper, 'l': str.lower, 't': str.title}
    try:
        with tempfile.NamedTemporaryFile(mode='w+', delete=True) as temp_file:
            with open(filename, 'r', encoding='utf-8') as file:
                is_mid_sentence = False
                for line in file:
                    if char_case == 's':
                        line, is_mid_sentence = to_sentence_case(
                            line, is_mid_sentence)
                        temp_file.write(line)
                    else:
                        temp_file.write(methods[char_case](line))
                # Flush the buffer to ensure content is fully written
                temp_file.flush()

            # Replace the original file with the temporary file
            try:
                shutil.copy(temp_file.name, filename)
            except PermissionError:
                print(f"{filename} is not writeable.")
    except PermissionError as exc:
        print(f'File is not writeable. {exc}')
    except OSError as exc:
        print(f"Error: {exc}")


def to_sentence_case(txt: str, continue_sentence: bool) -> tuple[str, bool]:
    """Convert to sentence case.

    Parameters
    ----------
    txt: str
        One line of text to convert.
    continue_sentence: bool
        True if mid-sentence, else False.

    Return
    ------
    str:
        The converted text.
    bool:
        True if mid-sentence else False.

    """
    print(txt, len(txt))
    completed_sentence = False
    try:
        if txt.strip()[-1] == '.':
            completed_sentence = True
    except IndexError:
        pass

    sentences = []
    for segment in txt.split('. '):
        if continue_sentence:
            sentences.append(segment.lower())
        else:
            sentences.append(segment.capitalize())

    return '. '.join(sentences).strip() + '\n', completed_sentence


def manual_config():
    """Configure options interactively.

    Called when app runs without commandline options.
    """
    print("Utility for converting a text file to upper or lower case.")
    print("(For command line options, run with '-h' switch.)\n")
    print("File names may be relative or fully qualified.")
    print("Enter 'Q' to Quit.\n")

    options = {"u": "upper", "l": "lower", "t": "title", "s": "sentence"}
    case_option = input_choice("Case (upper, lower, title, sentence [U/L/T/S]",
                               str(options.keys()))
    case_description = options[case_option]

    input_file = input_file_prompt()

    print(f"Converting {input_file} to {case_description}-case.")
    convert_case(input_file, case_option)


if __name__ == '__main__':
    manual_config()
