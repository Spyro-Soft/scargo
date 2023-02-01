from pathlib import Path

import pytest
from typer.testing import CliRunner

from scargo import cli

PRECONDITIONS = [
    "precondition_regression_tests",
    "precondition_regular_tests",
    "precondition_regression_tests_esp32",
    "precondition_regression_tests_stm32",
]


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_doc(precondition, request):
    request.getfixturevalue(precondition)
    doc_html_file = Path("build/doc/html/index.html")
    runner = CliRunner()

    result = runner.invoke(cli, ["doc"])
    assert result.exit_code == 0
    assert doc_html_file.is_file()
    