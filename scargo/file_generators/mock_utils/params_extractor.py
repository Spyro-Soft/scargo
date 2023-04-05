from typing import List

from clang.cindex import Cursor, CursorKind

from scargo.file_generators.mock_utils.data_classes import (
    ArgumentDescriptor,
    MockClassDescriptor,
    MockFunctionDescriptor,
    MockNamespaceDescriptor,
)


def extract_namespaces(cursor: Cursor, filename: str) -> List[MockNamespaceDescriptor]:
    return [
        MockNamespaceDescriptor(descendant.spelling)
        for descendant in cursor.walk_preorder()
        if descendant.kind == CursorKind.NAMESPACE
        and descendant.location.file == filename
    ]


def extract_classes(cursor: Cursor, filename: str) -> List[MockClassDescriptor]:
    return [
        MockClassDescriptor(
            cursor.spelling, f"Mock{cursor.spelling}", _extract_cxx_methods(cursor)
        )
        for descendant in cursor.walk_preorder()
        if descendant.kind == CursorKind.CLASS_DECL
        and descendant.location.file == filename
    ]


def _extract_cxx_methods(cursor: Cursor) -> List[MockFunctionDescriptor]:
    return [
        _extract_method_params(descendant)
        for descendant in cursor.walk_preorder()
        if descendant.kind == CursorKind.CXX_METHOD
        and cursor.access_specifier.name == "PUBLIC"
    ]


def _extract_method_params(
    cursor: Cursor,
) -> MockFunctionDescriptor:
    specifiers = []
    if cursor.is_virtual_method():
        specifiers.append("override")
    if cursor.is_const_method():
        specifiers.append("const")

    fun_args = [
        ArgumentDescriptor(descendant.spelling, descendant.type.spelling)
        for descendant in cursor.walk_preorder()
        if descendant.kind == CursorKind.PARM_DECL
    ]
    return MockFunctionDescriptor(
        name=cursor.spelling,
        return_type=cursor.result_type.spelling,
        specifiers=specifiers,
        arguments=fun_args,
    )
