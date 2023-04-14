from pathlib import Path

from clang.cindex import Index

from scargo.file_generators.clang_parser.data_classes import HeaderDescriptor
from scargo.file_generators.clang_parser.params_extractor import (
    extract_classes,
    extract_includes,
    extract_namespaces,
)


def parse_file(file_path: Path) -> HeaderDescriptor:
    """TODO documentation
    look here for available types which can be extracted
    https://clang.llvm.org/doxygen/group__CINDEX.html
    This function receives a path with file name as an argument and returns
    list of includes, i.e. every string that starts with "#include",
    dict of classes where keys are "public", "private" and "mock_class_name"
    and list of namespaces, i.e. strings that start with "namespace".
    """
    idx = Index.create()
    translation_unit = idx.parse(str(file_path), ["-x", "c++"])

    namespaces = extract_namespaces(translation_unit.cursor, str(file_path))
    classes = extract_classes(translation_unit.cursor, str(file_path))
    includes = extract_includes(translation_unit.cursor, str(file_path))
    return HeaderDescriptor(
        name=file_path.name, namespaces=namespaces, classes=classes, includes=includes
    )
