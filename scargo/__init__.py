# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #
import sys
from pathlib import Path
from typing import List, Optional

from typer import Argument, Option, Typer

__version__ = "1.0.3"

from scargo.scargo_src.global_values import DESCRIPTION, SCARGO_DEFAULT_CONFIG_FILE
from scargo.scargo_src.sc_build import scargo_build
from scargo.scargo_src.sc_check import scargo_check
from scargo.scargo_src.sc_clean import scargo_clean
from scargo.scargo_src.sc_config import ScargoTargets, Target
from scargo.scargo_src.sc_debug import scargo_debug
from scargo.scargo_src.sc_doc import scargo_doc
from scargo.scargo_src.sc_docker import scargo_docker
from scargo.scargo_src.sc_fix import scargo_fix
from scargo.scargo_src.sc_flash import scargo_flash
from scargo.scargo_src.sc_gen import scargo_gen
from scargo.scargo_src.sc_logger import get_logger
from scargo.scargo_src.sc_new import scargo_new
from scargo.scargo_src.sc_publish import scargo_publish
from scargo.scargo_src.sc_run import scargo_run
from scargo.scargo_src.sc_test import scargo_test
from scargo.scargo_src.sc_update import scargo_update
from scargo.scargo_src.sc_ver import scargo_version
from scargo.scargo_src.utils import get_config_file_path, get_project_root

###############################################################################


cli = Typer(context_settings=dict(help_option_names=["-h", "--help"]), help=DESCRIPTION)


###############################################################################


@cli.command()
def build(profile: str = Option("Debug", "--profile")):
    """Compile sources."""
    scargo_build(profile)


###############################################################################


@cli.command()
def check(  # pylint: disable=too-many-arguments
    clang_format: bool = Option(False, "--clang-format", help="Run clang-format."),
    clang_tidy: bool = Option(False, "--clang-tidy", help="Run clang-tidy."),
    copy_right: bool = Option(False, "--copyright", help="Run copyright check."),
    cppcheck: bool = Option(False, "--cppcheck", help="Run cppcheck."),
    cyclomatic: bool = Option(False, "--cyclomatic", help="Run python-lizard."),
    pragma: bool = Option(False, "--pragma", help="Run pragma check."),
    todo: bool = Option(False, "--todo", help="Run TODO check."),
    silent: bool = Option(False, "--silent", "-s", help="Show less output."),
):
    """Check source code in directory `src`."""
    scargo_check(
        clang_format,
        clang_tidy,
        copy_right,
        cppcheck,
        cyclomatic,
        pragma,
        todo,
        verbose=not silent,
    )


###############################################################################


@cli.command()
def clean():
    """Remove directory `build`."""
    scargo_clean()


###############################################################################


@cli.command()
def debug(
    bin_path: Optional[Path] = Option(
        None, "--bin", "-b", exists=True, dir_okay=False, help="Path to bin file"
    )
):
    """Use gdb cli to debug"""
    scargo_debug(bin_path)


###############################################################################


@cli.command()
def doc(open_doc: bool = Option(False, "--open", help="Open html documentation")):
    """Create project documentation"""
    scargo_doc(open_doc)


###############################################################################


docker = Typer(help="Manage the docker environment for the project")


@docker.command("build")
def docker_build(
    no_cache: bool = Option(
        False, "--no-cache", help="Do not use cache when building the docker image"
    ),
):
    """Build docker layers for this project depending on the target"""
    scargo_docker(build_docker=True, no_cache=no_cache)


@docker.command("run")
def docker_run():
    """Run project in docker environment"""
    scargo_docker(run_docker=True)


@docker.command("exec")
def docker_exec():
    """Attach to existing docker environment"""
    scargo_docker(exec_docker=True)


cli.add_typer(docker, name="docker")


###############################################################################


@cli.command()
def fix(
    clang_format: bool = Option(
        False, "--clang-format", help="Fix clang-format violations"
    ),
    copy_right: bool = Option(False, "--copyright", help="Fix copyrights violations"),
    pragma: bool = Option(False, "--pragma", help="Fix pragma violations"),
):
    """Fix violations reported by command `check`."""
    scargo_fix(pragma, copy_right, clang_format)


###############################################################################


@cli.command()
def flash(
    app: bool = Option(False, "--app", help="Flash app only"),
    file_system: bool = Option(False, "--fs", help="Flash filesystem only"),
    flash_profile: str = Option(
        "Debug", "--profile", help="Flash base on previously built profile"
    ),
):
    """Flash the target (only available for esp32 for now)."""
    scargo_flash(app, file_system, flash_profile)


###############################################################################


@cli.command()
def gen(  # pylint: disable=too-many-arguments
    profile: str = Option("Debug", "--profile", "-p"),
    gen_ut: Optional[Path] = Option(
        None,
        "--unit-test",
        "-u",
        exists=True,
        help="Generate unit test for chosen file or all headers in directory",
    ),
    gen_mock: Optional[Path] = Option(
        None,
        "--mock",
        "-m",
        exists=True,
        dir_okay=False,
        help="Generate mock of chosen file",
    ),
    certs: Optional[str] = Option(
        None,
        "--certs",
        "-c",
        metavar="<DEVICE ID>",
        help="Generate cert files for azure based on device ID.",
    ),
    file_system: bool = Option(
        False, "--fs", "-f", help="Build the filesystem, base on spiffs dir content."
    ),
    single_bin: bool = Option(
        False, "--bin", "-b", help="Generate single binary image."
    ),
):
    """Manage the auto file generator"""
    project_profile_path = get_project_root() / "build" / profile
    if (gen_ut is gen_mock is certs is None) and not (file_system or single_bin):
        logger = get_logger()
        logger.warning(
            "Please add one of the following options to the command:"
            "\n--unit-test\n--mock\n--certs\n--fs\n--bin"
        )
        sys.exit(1)

    scargo_gen(project_profile_path, gen_ut, gen_mock, certs, file_system, single_bin)


###############################################################################


@cli.command()
def new(  # pylint: disable=too-many-arguments
    name: str,
    bin_name: Optional[str] = Option(
        None,
        "--bin",
        help="Create binary target template.",
        prompt=True,
        prompt_required=False,
    ),
    lib_name: Optional[str] = Option(
        None,
        "--lib",
        help="Create library target template.",
        prompt=True,
        prompt_required=False,
    ),
    target: ScargoTargets = Option("x86", help="Target device."),
    create_docker: bool = Option(
        True, "--docker/--no-docker", help="Initialize docker environment."
    ),
    git: bool = Option(True, "--git/--no-git", help="Initialize git repository."),
):
    """Create new project template."""
    scargo_new(
        name,
        bin_name,
        lib_name,
        Target.get_target_by_id(target.value),
        create_docker,
        git,
    )
    scargo_update(Path(SCARGO_DEFAULT_CONFIG_FILE))


###############################################################################


@cli.command()
def publish(repo: str = Option("", "--repo", "-r", help="Repo name")):
    """Upload conan pkg to repo"""
    scargo_publish(repo)


###############################################################################


@cli.command()
def run(
    bin_path: Optional[Path] = Option(
        None, "--bin", "-b", exists=True, dir_okay=False, help="Path to bin file"
    ),
    profile: str = Option("Debug", "--profile", "-p"),
    skip_build: bool = Option(False, "--skip-build", help="Skip calling scargo build"),
    bin_params: List[str] = Argument(None),
):
    """Build and run project"""
    if not skip_build:
        scargo_build(profile)
    project_profile_path = get_project_root() / "build" / profile
    scargo_run(bin_path, project_profile_path, bin_params)


###############################################################################


@cli.command()
def test(verbose: bool = Option(False, "--verbose", "-v", help="Verbose mode.")):
    """Compile and run all tests in directory `test`."""
    scargo_test(verbose)


###############################################################################


@cli.command()
def update(
    config_file_path: Path = Option(
        SCARGO_DEFAULT_CONFIG_FILE,
        "--config-file",
        "-c",
        exists=True,
        dir_okay=False,
        help="Path to .toml configuration file.",
    ),
):
    """Read .toml config file and generate `CMakeLists.txt`."""
    scargo_update(get_config_file_path(config_file_path))


###############################################################################


@cli.command()
def version():
    """Get scargo version"""
    scargo_version()


###############################################################################

if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        print(f"\nA fatal error occurred: {e}")
        sys.exit(2)
