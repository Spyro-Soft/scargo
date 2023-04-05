#!/usr/bin/env python3
# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from pathlib import Path
from typing import List, Optional

from clang.cindex import Cursor, CursorKind, Index

from scargo.config import Config
from scargo.file_generators.base_gen import create_file_from_template
from scargo.file_generators.mock_utils.data_classes import (
    ArgumentDescriptor,
    HeaderDescriptor,
    MockClassDescriptor,
    MockFunctionDescriptor,
    MockNamespaceDescriptor,
)

MOCKS_DIR = "tests/mocks"


def generate_mocks(src_header: Path, src_dir: str, config: Config) -> bool:
    """
    Generates mock header and implementations for specified source headers.
    Creates directories and CMake lists where required.
    :param src_header Path to source directory or header
    :param src_dir source directory name (dependent on target)
    :param config
    """

    dst_header = get_mock_path(src_header, src_dir)

    # Skip generation if destination header exists
    if dst_header.is_file():
        return False

    template_and_output_paths = [
        ("mock/class_interface.h.j2", dst_header),
        ("mock/class_mock.h.j2", dst_header.with_name(f"mock_{dst_header.name}")),
        ("mock/class_mock.cpp.j2", dst_header.with_name(f"mock_{dst_header.stem}.cpp")),
    ]

    # Read classes and functions from the source header
    header_data = parse_file(src_header)

    for template_path, output_path in template_and_output_paths:
        create_file_from_template(
            template_path,
            output_path,
            template_params={"header": header_data},
            config=config,
        )

    return True


def get_mock_path(path: Path, src_dir: str) -> Path:
    parts: List[str] = list(path.parts)
    for i, part in enumerate(parts):
        if part == src_dir:
            parts[i] = MOCKS_DIR
            break
    return Path(*parts)


class ParamsExtractor:
    @staticmethod
    def extract_cxx_methods(cursor: Cursor) -> List[MockFunctionDescriptor]:
        descriptors = (
            ParamsExtractor._extract_method_params(descendant)
            for descendant in cursor.walk_preorder()
            if descendant.kind == CursorKind.CXX_METHOD
        )

        return [x for x in descriptors if x is not None]

    @staticmethod
    def extract_namespaces(
        cursor: Cursor, filename: str
    ) -> List[MockNamespaceDescriptor]:
        return [
            ParamsExtractor._extract_namespace_params(descendant)
            for descendant in cursor.walk_preorder()
            if descendant.kind == CursorKind.NAMESPACE
            and descendant.location.file == filename
        ]

    @staticmethod
    def extract_classes(cursor: Cursor, filename: str) -> List[MockClassDescriptor]:
        return [
            ParamsExtractor._extract_class_params(descendant)
            for descendant in cursor.walk_preorder()
            if descendant.kind == CursorKind.CLASS_DECL
            and descendant.location.file == filename
        ]

    @staticmethod
    def _extract_method_params(
        cursor: Cursor,
    ) -> Optional[MockFunctionDescriptor]:
        fun_ret_val = cursor.result_type.spelling
        fun_name = cursor.spelling
        fun_args = []
        specifiers = []

        if cursor.access_specifier.name != "PUBLIC":
            return None
        if cursor.is_virtual_method():
            specifiers.append("override")
        if cursor.is_const_method():
            specifiers.append("const")
        for i in cursor.walk_preorder():
            if i.kind == CursorKind.PARM_DECL:
                fun_args.append(ArgumentDescriptor(i.spelling, i.type.spelling))
        return MockFunctionDescriptor(
            fun_name, fun_ret_val, specifiers, arguments=fun_args
        )

    @staticmethod
    def _extract_namespace_params(cursor: Cursor) -> MockNamespaceDescriptor:
        return MockNamespaceDescriptor(cursor.spelling)

    @staticmethod
    def _extract_class_params(cursor: Cursor) -> MockClassDescriptor:
        cls = MockClassDescriptor(cursor.spelling, f"Mock{cursor.spelling}")
        cls.methods = ParamsExtractor.extract_cxx_methods(cursor)
        return cls


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
