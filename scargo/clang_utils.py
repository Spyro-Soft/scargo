from pathlib import Path
from typing import Iterable, Tuple

from clang import native  # type: ignore[attr-defined]
from clang.cindex import Config, Index, TokenKind

Config().set_library_file(str(Path(native.__file__).with_name("libclang.so")))


def get_comment_lines(file_path: Path) -> Iterable[Tuple[int, str]]:
    index = Index.create()
    translation_unit = index.parse(str(file_path), args=["-x", "c++"])

    for token in translation_unit.cursor.get_tokens():
        if token.kind == TokenKind.COMMENT:  # pylint: disable=no-member
            yield from enumerate(
                token.spelling.splitlines(keepends=False),
                start=token.extent.start.line,
            )
