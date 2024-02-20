"""Converts a text file to lower case.

Uses temporary file to allow processing files larger than RAM.
"""

import argparse
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
    print("(For command line options, run with '-h' switch.)")
    print("File names may be relative or fully qualified.")
    print("Enter 'Q' to Quit.\n")

    options = {"u": "upper", "l": "lower", "t": "title", "s": "sentence"}
    case_option = input_choice(
        "Change case to upper[U], lower[L], title[T], sentence[S]",
        str(str(options.keys())))
    case_description = options[case_option]

    input_file = input_file_prompt()

    print(f"Converting {input_file} to {case_description}-case.")
    convert_case(input_file, case_option)


def validate_options(args):
    """There must be no arguments, or filepath and one format specifier."""
    format_specifier = any([args.uppercase, args.lowercase,
                            args.title_case, args.sentence_case])
    if args.filepath and not format_specifier:
        parser.error(
            "at least one format option must be specified when "
            "specifying file path.")
    elif format_specifier and not args.filepath:
        parser.error(
            "File path must be passed when using command-line options.")


if __name__ == '__main__':
    usage_msg = ("[filepath [-u UPPERCASE | -l LOWERCASE | "
                 "-t TITLECASE | -s SENTENCECASE]]")

    parser = argparse.ArgumentParser(
        prog='textcase',
        description='Change the case of text in a file.'
        'Run without arguments for interactive mode.',
        usage=f'%(prog)s {usage_msg}')

    group = parser.add_argument_group(
        'Arguments',
        'Requires filepath + one other argument.')
    group.add_argument('filepath', nargs='?',
                       help='Path to the text file')
    exclusive_group = group.add_mutually_exclusive_group()
    exclusive_group.add_argument('-u', '--uppercase',
                                 action='store_true',
                                 help='Convert text to uppercase')
    exclusive_group.add_argument('-l', '--lowercase',
                                 action='store_true',
                                 help='Convert text to lowercase')
    exclusive_group.add_argument('-t', '--title-case',
                                 action='store_true',
                                 help='Convert text to title case')
    exclusive_group.add_argument('-s', '--sentence-case',
                                 action='store_true',
                                 help='Convert text to sentence case')
    args = parser.parse_args()

    validate_options(args)

    if args.filepath:
        print(args)
    else:
        manual_config()
