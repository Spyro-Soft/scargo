from pathlib import Path

from scargo.scargo_src.sc_gen import scargo_gen


def test_scargo_gen(create_new_project):
    scargo_gen(None, Path("src", "test_project.cpp"), None, None, None, None)
    expected_test_path = Path("tests", "ut", "ut_test_project.cpp")
    assert expected_test_path.is_file()
