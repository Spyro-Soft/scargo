#!/usr/bin/env python3
# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

import json
import os
from argparse import ArgumentParser
from pathlib import Path

import clang.cindex as cindex
from jinja2 import Environment, FileSystemLoader

from scargo.jinja.mock_utils.cmake_utlis import add_subdirs_to_cmake, create_cmake_lists
from scargo.jinja.mock_utils.data_classes import (
    ArgumentDescriptor,
    HeaderDescriptor,
    MockClassDescriptor,
    MockFunctionDescriptor,
    MockNamespaceDescriptor,
)
from scargo.jinja.mock_utils.error_classes import MockNotImplemented
from scargo.jinja.mock_utils.scraping_utils import missing_data_diff

# define paths
absolute_path = Path(__file__).parent.absolute()
SRC_DIR = "src"
MOCKS_DIR = "tests/mocks"

jinja_env = Environment(
    loader=FileSystemLoader(os.path.join(absolute_path, "mock_templates")),
    trim_blocks=True,
    lstrip_blocks=True,
)

# json where the mock paths are held, which lack of implementation has been accepted
missing_mocks_json = os.path.join(absolute_path, "mock_utils", "missing_mocks.json")


def option_parser_init():
    """This function parses the arguments which are given and
    returns known arguments for path and exclude and unknown arguments"""

    parser = ArgumentParser(epilog="The script creates mock files for cpp code.")

    parser.add_argument(
        "-p",
        "--path_to_src",
        type=str,
        default=SRC_DIR,
        help="Path to source directory or single header file",
    )

    parser.add_argument(
        "-e",
        "--exclude",
        default=[],
        action="append",
        help="Exclude directories",
    )

    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force mock folder override",
    )

    parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        help="Check if the mocks exist",
    )

    args = parser.parse_args()
    return args


def header_files_in_path(path_to_src, exclude, force, check_only, src_dir=SRC_DIR):
    """
    Returns list of the .h files in the path.
    If not check_only it also adds paths to the CMakelist.
    """
    header_files = []

    if os.path.isfile(path_to_src):
        root, file = os.path.split(path_to_src)
        mock_root = root.replace(src_dir, MOCKS_DIR, 1)
        if file.endswith(".h") or file.endswith(".hpp"):
            header_files.append((root, mock_root, file))
        else:
            print("Not a header file. Please chose .h or .hpp file.")

    if os.path.isdir(path_to_src):
        for root, _, files in os.walk(path_to_src):
            mock_root = root.replace(src_dir, MOCKS_DIR, 1)

            # Skip directories in the excluded directory list
            if exclude and root in exclude:
                print("Excluded:", root)
                continue

            for file in files:
                # We only consider files ending in .h
                if file.endswith(".h") or file.endswith(".hpp"):
                    header_files.append((root, mock_root, file))

            if check_only:
                continue

            # if tests/mocks in path doesn't exist then create it
            if not os.path.exists(mock_root):
                os.makedirs(mock_root)

            # generate CMakeLists if it does not exist or if forced
            if not os.path.isfile(mock_root + "/CMakeLists.txt") or force:
                # create CMakeLists file in root
                create_cmake_lists(mock_root, jinja_env)

            # add subdirs to CMakeLists
            add_subdirs_to_cmake(mock_root)

    return header_files


def check_mocks(path_to_src, exclude, force, check_only):
    """
    Check if there is a mock implementations for cpp files in the path.
    """
    src_dir = "main" if "main" in path_to_src else SRC_DIR
    header_files = header_files_in_path(
        path_to_src, exclude, force, check_only, src_dir
    )
    missing_mocks = []
    missing_classes = {}
    missing_methods = {}

    for root, mock_root, file in header_files:
        src_header = os.path.join(root, file)
        dst_header = os.path.join(mock_root, file)

        # Skip files in the excluded list
        if exclude and src_header in exclude:
            print("Excluded:", src_header)
            continue

        # Scraping data from exist source and mock files to compare
        if os.path.isfile(dst_header):
            # Read classes and functions from the source header
            header_data = parse_file(src_header)
            # Check classes and methods in mock file
            mock_file = open(dst_header, "r", encoding="utf-8").read()
            for mock_class in header_data.classes:
                if mock_class.name and mock_class.name not in mock_file:
                    missing_classes.setdefault(src_header, []).append(mock_class.name)
                    continue
                for method in mock_class.methods:
                    if method.name not in mock_file:
                        missing_methods.setdefault(src_header, []).append(method.name)
            for mock_class in header_data.one_line_classes:
                mock_class = mock_class.strip().replace(";", "")
                if mock_class not in mock_file:
                    missing_classes.setdefault(src_header, []).append(mock_class)
        else:
            missing_mocks.append(src_header)

    data = {
        "missing_mocks": missing_mocks,
        "missing_classes": missing_classes,
        "missing_methods": missing_methods,
    }

    with open(missing_mocks_json, "r", encoding="utf-8") as json_file:
        old_data = json.load(json_file)

    if missing_data_diff(old_data, data):
        raise MockNotImplemented()


def generate_mocks(path_to_src: Path, exclude=(), force=False, check_only=False):
    """
    Generates mock header and implementations for specified source headers.
    Creates directories and CMake lists where required.
    :param path_to_src Path to source directory or header
    :param exclude List of files or directories to exclude from mock generator
    :param force Force overwrite
    :param check_only
    """
    src_dir = path_to_src.parent.name
    header_files = header_files_in_path(
        path_to_src, exclude, force, check_only, src_dir
    )

    for root, mock_root, file in header_files:

        src_header = os.path.join(root, file)
        dst_header = os.path.join(mock_root, file)
        dst_mock = os.path.join(mock_root, f"mock_{file}")

        # Skip files in the excluded list
        if exclude and src_header in exclude:
            print("Excluded:", src_header)
            continue

        # Skip generation if destination header exists
        if os.path.isfile(dst_header):
            print("Skipping:", src_header)
            continue

        # Read classes and functions from the source header
        header_data = parse_file(src_header)

        # generate public interface header
        with open(dst_header, "w", encoding="utf-8") as out:
            out.write(
                jinja_env.get_template("class_interface.h.j2").render(
                    header=header_data
                )
            )

        # generate mock header
        with open(dst_mock, "w", encoding="utf-8") as out:
            out.write(
                jinja_env.get_template("class_mock.h.j2").render(header=header_data)
            )

        # generate mock implementation
        with open(dst_mock.replace(".h", ".cpp"), "w", encoding="utf-8") as out:
            out.write(
                jinja_env.get_template("class_mock.cpp.j2").render(header=header_data)
            )

        print("Generated:", src_header)


def find_namespaces_in_file(cursor, filename):
    for i in cursor.walk_preorder():
        if i.kind != cindex.CursorKind.NAMESPACE:
            continue
        if i.location.file.name != filename:
            continue
        yield i.spelling


class ParamsExtractor(object):
    @staticmethod
    def extract_params_of_children_in_file(cursor, type_list, filename=None):
        return [
            ParamsExtractor.extract_params(x)
            for x in ParamsExtractor.find_children_of_type_in_file(
                cursor, type_list, filename
            )
        ]

    @staticmethod
    def find_children_of_type_in_file(cursor, type_list, filename=None):
        for i in cursor.walk_preorder():
            if i.kind not in type_list:
                continue
            if filename is not None and i.location.file.name != filename:
                continue
            yield i

    @staticmethod
    def extract_params(cursor):
        if cursor.kind == cindex.CursorKind.FUNCTION_DECL:
            return __class__._extract_function_params(cursor)
        elif cursor.kind == cindex.CursorKind.CXX_METHOD:
            return __class__._extract_method_params(cursor)
        elif cursor.kind == cindex.CursorKind.CONSTRUCTOR:
            return __class__._extract_method_params(cursor)
        elif cursor.kind == cindex.CursorKind.DESTRUCTOR:
            return __class__._extract_method_params(cursor)
        elif cursor.kind == cindex.CursorKind.CLASS_DECL:
            return __class__._extract_class_params(cursor)
        elif cursor.kind == cindex.CursorKind.NAMESPACE:
            return __class__._extract_namespace_params(cursor)

    @staticmethod
    def _extract_method_params(cursor):
        fun_ret_val = cursor.result_type.spelling
        fun_name = cursor.spelling
        fun_args = []
        specifiers = []

        if cursor.access_specifier.name != "PUBLIC":
            return
        if cursor.is_virtual_method():
            specifiers.append("override")
        if cursor.is_const_method():
            specifiers.append("const")
        for i in cursor.walk_preorder():
            if i.kind == cindex.CursorKind.PARM_DECL:
                fun_args.append(ArgumentDescriptor(i.spelling, i.type.spelling))
        return MockFunctionDescriptor(
            fun_name, fun_ret_val, specifiers, arguments=fun_args
        )

    @staticmethod
    def _extract_function_params(cursor):
        fun_ret_val = cursor.result_type.spelling
        fun_name = cursor.spelling
        fun_args = []
        for i in cursor.walk_preorder():
            if i.kind == cindex.CursorKind.PARM_DECL:
                fun_args.append(ArgumentDescriptor(i.spelling, i.type.spelling))
        return MockFunctionDescriptor(fun_name, fun_ret_val, "", arguments=fun_args)

    @staticmethod
    def _extract_namespace_params(cursor):
        return MockNamespaceDescriptor(cursor.spelling)

    @staticmethod
    def _extract_class_params(cursor):
        cls = MockClassDescriptor(cursor.spelling, f"Mock{cursor.spelling}")

        methods = ParamsExtractor.find_children_of_type_in_file(
            cursor, [cindex.CursorKind.CXX_METHOD]
        )

        cls.methods = [ParamsExtractor.extract_params(m) for m in methods]

        # delete Nones from lists
        cls.methods = [x for x in cls.methods if x is not None]
        return cls


def parse_file(file_path):
    """TODO documentation
    look here for available types which can be extracted
    https://clang.llvm.org/doxygen/group__CINDEX.html
    This function receives a path with file name as an argument and returns
    list of includes, i.e. every string that starts with "#include",
    dict of classes where keys are "public", "private" and "mock_class_name"
    and list of namespaces, i.e. strings that start with "namespace".
    """
    file_name = os.path.basename(file_path)

    hdr = HeaderDescriptor(file_name)

    idx = cindex.Index.create()
    translation_unit = idx.parse(file_path, ["-x", "c++"])

    hdr.namespaces = ParamsExtractor.extract_params_of_children_in_file(
        translation_unit.cursor, [cindex.CursorKind.NAMESPACE], file_path
    )

    # defns = params_extractor.find_children_of_type_in_file(
    #     translation_unit.cursor, [cindex.CursorKind.FUNCTION_DECL], file_path
    # )

    hdr.classes = ParamsExtractor.extract_params_of_children_in_file(
        translation_unit.cursor, [cindex.CursorKind.CLASS_DECL], file_path
    )
    return hdr


def main():
    args = option_parser_init()

    if args.check and args.force:
        raise ValueError("You shouldn't use the check and force option together.")
    if args.check:
        check_mocks(args.path_to_src, args.exclude, args.force, args.check)
        pass
    else:
        generate_mocks(args.path_to_src, args.exclude, args.force, args.check)


if __name__ == "__main__":
    main()
