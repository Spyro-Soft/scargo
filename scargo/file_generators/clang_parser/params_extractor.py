from typing import List

from clang.cindex import Cursor, CursorKind

from scargo.file_generators.clang_parser.data_classes import (
    ArgumentDescriptor,
    ClassDescriptor,
    FunctionDescriptor,
    IncludeDescriptor,
    NamespaceDescriptor,
)


def extract_namespaces(cursor: Cursor, filename: str) -> List[NamespaceDescriptor]:
    return [
        NamespaceDescriptor(descendant.spelling)
        for descendant in cursor.walk_preorder()
        if descendant.kind == CursorKind.NAMESPACE
        # remove type ignore after fix is relased:
        # https://github.com/tgockel/types-clang/issues/10
        and descendant.location.file.name == filename  # type: ignore[attr-defined]
    ]


def extract_classes(cursor: Cursor, filename: str) -> List[ClassDescriptor]:
    return [
        ClassDescriptor(
            descendant.spelling,
            f"Mock{descendant.spelling}",
            _extract_cxx_methods(descendant),
        )
        for descendant in cursor.walk_preorder()
        if descendant.kind == CursorKind.CLASS_DECL
        and descendant.location.file.name == filename  # type: ignore[attr-defined]
    ]


def extract_includes(cursor: Cursor, filename: str) -> List[IncludeDescriptor]:
    return [
        IncludeDescriptor(descendant.displayname)
        for descendant in cursor.walk_preorder()
        if descendant.kind == CursorKind.INCLUSION_DIRECTIVE
        and descendant.location.file.name == filename  # type: ignore[attr-defined]
    ]


def _extract_cxx_methods(cursor: Cursor) -> List[FunctionDescriptor]:
    return [
        _extract_method_params(descendant)
        for descendant in cursor.walk_preorder()
        if descendant.kind == CursorKind.CXX_METHOD
        and descendant.access_specifier.name == "PUBLIC"
    ]


def _extract_method_params(
    cursor: Cursor,
) -> FunctionDescriptor:
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
    return FunctionDescriptor(
        name=cursor.spelling,
        return_type=cursor.result_type.spelling,
        specifiers=specifiers,
        arguments=fun_args,
    )
