from pathlib import Path

from clang.cindex import Index

from scargo.file_generators.mock_utils.data_classes import HeaderDescriptor
from scargo.file_generators.mock_utils.params_extractor import ParamsExtractor


def parse_file(file_path: Path) -> HeaderDescriptor:
    """TODO documentation
    look here for available types which can be extracted
    https://clang.llvm.org/doxygen/group__CINDEX.html
    This function receives a path with file name as an argument and returns
    list of includes, i.e. every string that starts with "#include",
    dict of classes where keys are "public", "private" and "mock_class_name"
    and list of namespaces, i.e. strings that start with "namespace".
    """
    file_name = file_path.name

    hdr = HeaderDescriptor(file_name)

    idx = Index.create()
    translation_unit = idx.parse(str(file_path), ["-x", "c++"])

    hdr.namespaces = ParamsExtractor.extract_namespaces(
        translation_unit.cursor, str(file_path)
    )
    hdr.classes = ParamsExtractor.extract_classes(
        translation_unit.cursor, str(file_path)
    )
    return hdr
