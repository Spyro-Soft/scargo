# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #
from typing import List, Sequence


class ArgumentDescriptor:
    """Describes a function argument"""

    def __init__(self, name: str, data_type: str):
        self.name = name
        self.data_type = data_type


class FunctionDescriptor:
    """Contains function name and types"""

    def __init__(
        self,
        name: str,
        return_type: str,
        specifiers: Sequence[str],
        arguments: Sequence[ArgumentDescriptor] = (),
    ):
        self.name = name
        self.return_type = return_type
        self.specifiers = specifiers
        self.arguments = arguments

        for _, arg in enumerate(self.arguments):
            if not arg.name:
                arg.name = ""

    def get_specifiers(self) -> str:
        return ", ".join(spec for spec in self.specifiers)

    def get_typed_args(self) -> str:
        for arg in self.arguments:
            if arg.data_type == "void":
                return " "
        return ", ".join(arg.data_type + " " + arg.name for arg in self.arguments)

    def get_arg_names(self) -> str:
        return ", ".join(arg.name for arg in self.arguments)

    def get_arg_types(self) -> str:
        for arg in self.arguments:
            if arg.data_type == "void":
                return " "
        return ", ".join(arg.data_type for arg in self.arguments)


class ClassDescriptor:
    """Contains class names and function definitions"""

    def __init__(self, name: str, mock_name: str, methods: List[FunctionDescriptor]):
        self.name = name
        self.mock_name = mock_name
        self.methods: List[FunctionDescriptor] = methods


class NamespaceDescriptor:
    def __init__(self, name: str):
        self.name = name


class IncludeDescriptor:
    def __init__(self, name: str):
        self.name = name


class HeaderDescriptor:
    """Parsed header definitions"""

    def __init__(
        self,
        name: str,
        classes: List[ClassDescriptor],
        namespaces: List[NamespaceDescriptor],
        includes: List[IncludeDescriptor],
    ):
        self.name = name
        self.classes = classes
        self.namespaces = namespaces
        self.includes = includes
