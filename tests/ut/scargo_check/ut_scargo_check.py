from typing import Dict
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from scargo.commands import check
from scargo.commands.check import scargo_check
from scargo.config import Config

CHECKERS = [
    check.PragmaChecker,
    check.CopyrightChecker,
    check.TodoChecker,
    check.ClangFormatChecker,
    check.ClangTidyChecker,
    check.CyclomaticChecker,
    check.CppcheckChecker,
]


@pytest.fixture
def mock_checkers(mocker: MockerFixture) -> Dict[str, MagicMock]:
    checkers = {
        checker_class.check_name: mocker.patch(f"{scargo_check.__module__}.{checker_class.__name__}")
        for checker_class in CHECKERS
    }
    for name, checker in checkers.items():
        checker.check_name = name
        checker().check.return_value = 0
    return checkers


@pytest.fixture
def mock_prepare_config(mocker: MockerFixture, config: Config) -> MagicMock:
    return mocker.patch(f"{scargo_check.__module__}.prepare_config", return_value=config)


def test_scargo_check_single(
    mock_checkers: Dict[str, MagicMock],
    mock_prepare_config: MagicMock,
    config: Config,
) -> None:
    scargo_check(
        clang_format=True,
        clang_tidy=False,
        copy_right=False,
        cppcheck=False,
        cyclomatic=False,
        pragma=False,
        todo=False,
        verbose=False,
    )

    assert mock_checkers["clang-format"]().check.call_count == 1
    assert mock_checkers["clang-tidy"]().check.call_count == 0
    assert mock_checkers["copyright"]().check.call_count == 0
    assert mock_checkers["cppcheck"]().check.call_count == 0
    assert mock_checkers["cyclomatic"]().check.call_count == 0
    assert mock_checkers["pragma"]().check.call_count == 0
    assert mock_checkers["todo"]().check.call_count == 0


def test_scargo_check_all(
    mock_checkers: Dict[str, MagicMock],
    mock_prepare_config: MagicMock,
) -> None:
    scargo_check(
        clang_format=True,
        clang_tidy=True,
        copy_right=True,
        cppcheck=True,
        cyclomatic=True,
        pragma=True,
        todo=True,
        verbose=False,
    )

    assert mock_checkers["clang-format"]().check.call_count == 1
    assert mock_checkers["clang-tidy"]().check.call_count == 1
    assert mock_checkers["copyright"]().check.call_count == 1
    assert mock_checkers["cppcheck"]().check.call_count == 1
    assert mock_checkers["cyclomatic"]().check.call_count == 1
    assert mock_checkers["pragma"]().check.call_count == 1
    assert mock_checkers["todo"]().check.call_count == 1


def test_scargo_check_default(
    mock_checkers: Dict[str, MagicMock],
    mock_prepare_config: MagicMock,
) -> None:
    scargo_check(
        clang_format=False,
        clang_tidy=False,
        copy_right=False,
        cppcheck=False,
        cyclomatic=False,
        pragma=False,
        todo=False,
        verbose=False,
    )

    assert mock_checkers["clang-format"]().check.call_count == 1
    assert mock_checkers["clang-tidy"]().check.call_count == 1
    assert mock_checkers["copyright"]().check.call_count == 1
    assert mock_checkers["cppcheck"]().check.call_count == 1
    assert mock_checkers["cyclomatic"]().check.call_count == 1
    assert mock_checkers["pragma"]().check.call_count == 1
    assert mock_checkers["todo"]().check.call_count == 1
