from typing import List, Optional

from clang.cindex import Cursor, CursorKind

from scargo.file_generators.mock_utils.data_classes import (
    ArgumentDescriptor,
    MockClassDescriptor,
    MockFunctionDescriptor,
    MockNamespaceDescriptor,
)


def _extract_cxx_methods(cursor: Cursor) -> List[MockFunctionDescriptor]:
    descriptors = (
        _extract_method_params(descendant)
        for descendant in cursor.walk_preorder()
        if descendant.kind == CursorKind.CXX_METHOD
    )

    return [x for x in descriptors if x is not None]


def extract_namespaces(cursor: Cursor, filename: str) -> List[MockNamespaceDescriptor]:
    return [
        _extract_namespace_params(descendant)
        for descendant in cursor.walk_preorder()
        if descendant.kind == CursorKind.NAMESPACE
        and descendant.location.file == filename
    ]


def extract_classes(cursor: Cursor, filename: str) -> List[MockClassDescriptor]:
    return [
        _extract_class_params(descendant)
        for descendant in cursor.walk_preorder()
        if descendant.kind == CursorKind.CLASS_DECL
        and descendant.location.file == filename
    ]


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
    return MockFunctionDescriptor(fun_name, fun_ret_val, specifiers, arguments=fun_args)


def _extract_namespace_params(cursor: Cursor) -> MockNamespaceDescriptor:
    return MockNamespaceDescriptor(cursor.spelling)


def _extract_class_params(cursor: Cursor) -> MockClassDescriptor:
    cls = MockClassDescriptor(cursor.spelling, f"Mock{cursor.spelling}")
    cls.methods = _extract_cxx_methods(cursor)
    return cls
