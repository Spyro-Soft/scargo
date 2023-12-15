import re
from pathlib import Path
from typing import Iterable, List, Tuple


def finditer_with_line_numbers(
    pattern: re.Pattern, string: str, flags: int = 0  # type: ignore[type-arg]
) -> Iterable[Tuple[re.Match, int]]:  # type: ignore[type-arg]
    """
    Version of re.finditer that additionally returns the line number for each match.

    :param pattern: A compiled regular expression pattern.
    :param string: The string to be searched.
    :param flags: Standard re flags to modify the regex behavior
    :yield: Tuples of (match object, line number), where line number is the line on which the match starts.
    """
    matches = list(re.finditer(pattern, string, flags))
    if not matches:
        return

    end = matches[-1].start()
    newline_table = {-1: 0}
    for i, m in enumerate(re.finditer("\\n", string), 1):
        offset = m.start()
        if offset > end:
            break
        newline_table[offset] = i

    for m in matches:
        newline_offset = string.rfind("\n", 0, m.start())
        line_number = newline_table[newline_offset]
        yield (m, line_number)


def extract_block_comments(content: str) -> List[str]:
    """
    Extracts block comments from the given content.

    :param content: The string to extract comments from.
    :return: A list of block comments.
    """
    pattern = re.compile(r"/\*[\s\S]*?\*/", re.DOTALL)
    return pattern.findall(content)


def extract_grouped_line_comments(content: str) -> List[str]:
    """
    Extracts and groups line comments from the given content.

    :param content: The string to extract comments from.
    :param pattern: The compiled regex pattern for line comments.
    :return: A list of grouped line comments.
    """
    pattern = re.compile(r"//.*", re.MULTILINE)
    grouped_comments = []
    current_section: List[Tuple[str, int]] = []

    for comment, line_number in finditer_with_line_numbers(pattern, content):
        if current_section and line_number > current_section[-1][1] + 1:
            grouped_comments.append(
                "\n".join(comment[0] for comment in current_section)
            )
            current_section = []
        current_section.append((comment.group(), line_number))

    if current_section:
        grouped_comments.append("\n".join(comment[0] for comment in current_section))

    return grouped_comments


def extract_comment_sections(file_path: Path) -> List[str]:
    """
    Extracts comment sections from the given file.

    :param file_path: A Path object pointing to the file.
    :return: A list of comment sections.
    """
    content = file_path.read_text()

    block_comments = extract_block_comments(content)
    grouped_line_comments = extract_grouped_line_comments(content)

    return block_comments + grouped_line_comments
