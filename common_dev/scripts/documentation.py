import subprocess
from pathlib import Path


def create_doc():
    project_path = Path().absolute()
    docs_path = Path(project_path, "docs")
    subprocess.check_call(
        "sphinx-apidoc ../scargo -o source/modules/ -f", shell=True, cwd=docs_path
    )
    subprocess.check_call("make html", shell=True, cwd=docs_path)
