import io
import os
import re
import sys

try:
    from setuptools import find_packages, setup
except ImportError:
    print(
        "Package setuptools is missing from your Python installation. "
        "Please see the installation section in the scargo documentation"
        " for instructions on how to install it."
    )
    exit(1)


def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8"),
    ) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def main():
    long_description = """
    ==========
    scargo
    ==========
    A Python-based, open-source, platform-independent utility manage C/C++ package and \
    software development life cycle.
    
    The scargo project is `hosted on github <https://spyro-soft.github.io/scargo/>`_.
    
    Documentation
    -------------
    Visit online documentation
    
    Contributing
    ------------
    Spyrosoft Solution S.A members.
    """

    version_file = "scargo/scargo_src/global_values.py"
    version_str_line = open(version_file, "rt").read()
    version_pattern = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(version_pattern, version_str_line, re.M)
    if mo:
        version_str = mo.group(1)
    else:
        raise RuntimeError("Unable to find version string in %s." % (version_file,))

    setup(
        name="scargo",
        version=version_str,
        description="C/C++ package manager and software development life cycle which base on RUST cargo idea.",
        long_description=long_description,
        url="https://github.com/Spyro-Soft/scargo",
        project_urls={
            "Documentation": "https://github.com/Spyro-Soft/scargo/tree/main/docs",
            "Source": "https://github.com/Spyro-Soft/scargo/tree/main/scargo",
            "Tracker": "https://github.com/Spyro-Soft/scargo/issues",
        },
        author="Spyrosoft Solutions S.A.",
        author_email="aak@spyro-soft.com",
        license="MIT",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "Natural Language :: English",
            "Operating System :: POSIX",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: MacOS :: MacOS X",
            "Topic :: Software Development :: Embedded Systems",
            "Environment :: Console",
            "License :: OSI Approved :: MIT",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
        ],
        python_requires=">=3.7",
        setup_requires=(["wheel"] if "bdist_wheel" in sys.argv else []),
        extras_require={
            "dev": [
                "flake8>=3.2.0",
                "flake8-gl-codeclimate",
                "pyelftools",
                "unittest-xml-reporting",
                "coverage~=6.0",
                "black",
                "isort==5.11.4",
                "pre-commit",
                "requests>=2.28.1",
                "pylint",
                "gcovr>=5.2",
                "PyInstaller",
                "pytest",
                "pytest-bdd",
                "pytest-subprocess",
                "pytest-cov",
                "allure-pytest",
                "pyclean==2.2.0",
                "allure-docx @ git+https://github.com/typhoon-hil/allure-docx@54ad0c3e",
            ],
            "doc": [
                "recommonmark",
                "Sphinx",
                "sphinx-rtd-theme==1.1.1",
                "sphinxcontrib-plantuml==0.24.1",
            ],
        },
        install_requires=[
            "docker==6.0.1",
            "typer==0.7.0",
            "toml==0.10.2",
            "jinja2==3.1.2",
            "conan==1.56.0",
            "docker-compose==1.29.2",
            "coloredlogs==15.0.1",
            "libclang==15.0.6.1",
            "clang==14.0",
            "lizard==1.17.10",
            "cmake==3.25.0",
            "shellingham==1.5.0.post1",
            "esptool==4.4",
            "tomlkit==0.11.6",
            "pydantic==1.10.4",
        ],
        packages=find_packages(),
        include_package_data=True,
        package_data={"": ["scargo/*"]},
        entry_points={
            "console_scripts": [
                "scargo = scargo.__init__:cli",
            ],
        }
    )


if __name__ == '__main__':
    main()
