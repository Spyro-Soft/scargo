# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #
import os
import sys
from pathlib import Path
from typing import List, Optional

from typer import Argument, Option, Typer

from scargo.commands.build import scargo_build
from scargo.commands.check import scargo_check
from scargo.commands.clean import scargo_clean
from scargo.commands.debug import scargo_debug
from scargo.commands.doc import scargo_doc
from scargo.commands.docker import (
    scargo_docker_build,
    scargo_docker_exec,
    scargo_docker_run,
)
from scargo.commands.fix import scargo_fix
from scargo.commands.flash import scargo_flash
from scargo.commands.gen import scargo_gen
from scargo.commands.new import scargo_new
from scargo.commands.publish import scargo_publish
from scargo.commands.run import scargo_run
from scargo.commands.test import scargo_test
from scargo.commands.update import scargo_update
from scargo.commands.version import scargo_version
from scargo.config import ScargoTargets, Target
from scargo.global_values import DESCRIPTION, SCARGO_DEFAULT_CONFIG_FILE
from scargo.logger import get_logger
from scargo.path_utils import get_config_file_path

logger = get_logger()

###############################################################################


cli = Typer(context_settings={"help_option_names": ["-h", "--help"]}, help=DESCRIPTION)


BASE_DIR_OPTION = Option(
    None,
    "--base-dir",
    "-B",
    exists=True,
    file_okay=False,
    help="Base directory of the project",
)


###############################################################################


@cli.command()
def build(
    profile: str = Option("Debug", "--profile"),
    base_dir: Optional[Path] = BASE_DIR_OPTION,
) -> None:
    """Compile sources."""
    if base_dir:
        os.chdir(base_dir)
    scargo_build(profile)


###############################################################################


@cli.command()
def check(
    clang_format: bool = Option(False, "--clang-format", help="Run clang-format."),
    clang_tidy: bool = Option(False, "--clang-tidy", help="Run clang-tidy."),
    copy_right: bool = Option(False, "--copyright", help="Run copyright check."),
    cppcheck: bool = Option(False, "--cppcheck", help="Run cppcheck."),
    cyclomatic: bool = Option(False, "--cyclomatic", help="Run python-lizard."),
    pragma: bool = Option(False, "--pragma", help="Run pragma check."),
    todo: bool = Option(False, "--todo", help="Run TODO check."),
    silent: bool = Option(False, "--silent", "-s", help="Show less output."),
    base_dir: Optional[Path] = BASE_DIR_OPTION,
) -> None:
    """Check source code in directory `src`."""
    if base_dir:
        os.chdir(base_dir)
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
def clean(base_dir: Optional[Path] = BASE_DIR_OPTION) -> None:
    """Remove directory `build`."""
    if base_dir:
        os.chdir(base_dir)
    scargo_clean()


###############################################################################


@cli.command()
def debug(
    bin_path: Optional[Path] = Option(
        None,
        "--bin",
        "-b",
        exists=True,
        dir_okay=False,
        resolve_path=True,
        help="Path to bin file",
    ),
    base_dir: Optional[Path] = BASE_DIR_OPTION,
) -> None:
    """Use gdb cli to debug"""
    if base_dir:
        os.chdir(base_dir)
    scargo_debug(bin_path)


###############################################################################


@cli.command()
def doc(
    open_doc: bool = Option(False, "--open", help="Open html documentation"),
    base_dir: Optional[Path] = BASE_DIR_OPTION,
) -> None:
    """Create project documentation"""
    if base_dir:
        os.chdir(base_dir)
    scargo_doc(open_doc)


###############################################################################


docker = Typer(help="Manage the docker environment for the project")


@docker.command(
    "build", context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def docker_build(
    docker_opts: List[str] = Argument(None), base_dir: Optional[Path] = BASE_DIR_OPTION
) -> None:
    """Build docker layers for this project depending on the target"""
    if base_dir:
        os.chdir(base_dir)
    scargo_docker_build(docker_opts)


@docker.command(
    "run", context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def docker_run(
    command: str = Option(
        "bash",
        "-c",
        "--command",
        metavar="COMMAND",
        help="Select command to be used with docker run.",
    ),
    base_dir: Optional[Path] = BASE_DIR_OPTION,
    docker_opts: List[str] = Argument(None),
) -> None:
    """Run project in docker environment"""
    if base_dir:
        os.chdir(base_dir)
    scargo_docker_run(docker_opts=docker_opts, command=command)


@docker.command(
    "exec", context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def docker_exec(
    base_dir: Optional[Path] = BASE_DIR_OPTION, docker_opts: List[str] = Argument(None)
) -> None:
    """Attach to existing docker environment"""
    if base_dir:
        os.chdir(base_dir)
    scargo_docker_exec(docker_opts)


cli.add_typer(docker, name="docker")


###############################################################################


@cli.command()
def fix(
    clang_format: bool = Option(
        False, "--clang-format", help="Fix clang-format violations"
    ),
    copy_right: bool = Option(False, "--copyright", help="Fix copyrights violations"),
    pragma: bool = Option(False, "--pragma", help="Fix pragma violations"),
    base_dir: Optional[Path] = BASE_DIR_OPTION,
) -> None:
    """Fix violations reported by command `check`."""
    if base_dir:
        os.chdir(base_dir)
    scargo_fix(pragma, copy_right, clang_format)


###############################################################################


@cli.command()
def flash(
    app: bool = Option(False, "--app", help="Flash app only"),
    file_system: bool = Option(False, "--fs", help="Flash filesystem only"),
    flash_profile: str = Option(
        "Debug", "--profile", help="Flash base on previously built profile"
    ),
    port: Optional[str] = Option(
        None,
        help="(esp32 only) port where the target device of the command is connected to, e.g. /dev/ttyUSB0",
    ),
    no_erase: bool = Option(False, help="(stm32 only) Don't erase target memory"),
    base_dir: Optional[Path] = BASE_DIR_OPTION,
) -> None:
    """Flash the target."""
    if base_dir:
        os.chdir(base_dir)
    scargo_flash(app, file_system, flash_profile, port, not no_erase)


###############################################################################


@cli.command()
def gen(
    profile: str = Option("Debug", "--profile", "-p"),
    gen_ut: Optional[Path] = Option(
        None,
        "--unit-test",
        "-u",
        exists=True,
        resolve_path=True,
        help="Generate unit test for chosen file or all headers in directory",
    ),
    gen_mock: Optional[Path] = Option(
        None,
        "--mock",
        "-m",
        exists=True,
        dir_okay=False,
        resolve_path=True,
        help="Generate mock of chosen file",
    ),
    certs: Optional[str] = Option(
        None,
        "--certs",
        "-c",
        metavar="<DEVICE ID>",
        help="Generate cert files for azure based on device ID.",
    ),
    certs_mode: Optional[str] = Option(
        None,
        "--type",
        "-t",
        metavar="[all, device]",
        help="Mode for generating certificates.",
    ),
    certs_input: Optional[Path] = Option(
        None,
        "--in",
        "-i",
        dir_okay=True,
        resolve_path=True,
        help="Directory with root and intermediate certificates.",
    ),
    certs_passwd: Optional[str] = Option(
        None,
        "--passwd",
        "-p",
        metavar="<PASSWORD>",
        help="Password to be set for generated certificates",
    ),
    file_system: bool = Option(
        False, "--fs", "-f", help="Build the filesystem, base on spiffs dir content."
    ),
    single_bin: bool = Option(
        False, "--bin", "-b", help="Generate single binary image."
    ),
    base_dir: Optional[Path] = BASE_DIR_OPTION,
) -> None:
    """Manage the auto file generator"""
    if base_dir:
        os.chdir(base_dir)
    if (gen_ut is gen_mock is certs is None) and not (file_system or single_bin):
        logger.warning(
            "Please add one of the following options to the command:"
            "\n--unit-test\n--mock\n--certs\n--fs\n--bin"
        )
        sys.exit(1)

    scargo_gen(
        profile,
        gen_ut,
        gen_mock,
        certs,
        certs_mode,
        certs_input,
        certs_passwd,
        file_system,
        single_bin,
    )


###############################################################################


@cli.command()
def new(
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
    base_dir: Optional[Path] = BASE_DIR_OPTION,
) -> None:
    """Create new project template."""
    if base_dir:
        os.chdir(base_dir)
    scargo_new(
        name,
        bin_name,
        lib_name,
        Target.get_target_by_id(target.value),
        create_docker,
        git,
    )
    scargo_update(Path(name, SCARGO_DEFAULT_CONFIG_FILE).absolute())


###############################################################################


@cli.command()
def publish(
    repo: str = Option("", "--repo", "-r", help="Repo name"),
    profile: str = Option("Release", "--profile", "-p"),
    base_dir: Optional[Path] = BASE_DIR_OPTION,
) -> None:
    """Upload conan pkg to repo"""
    if base_dir:
        os.chdir(base_dir)
    scargo_publish(repo, profile)


###############################################################################


@cli.command()
def run(
    bin_path: Optional[Path] = Option(
        None,
        "--bin",
        "-b",
        exists=True,
        dir_okay=False,
        resolve_path=True,
        help="Path to bin file",
    ),
    profile: str = Option("Debug", "--profile", "-p"),
    skip_build: bool = Option(False, "--skip-build", help="Skip calling scargo build"),
    bin_params: List[str] = Argument(None),
    base_dir: Optional[Path] = BASE_DIR_OPTION,
) -> None:
    """Build and run project"""
    if base_dir:
        os.chdir(base_dir)
    if not skip_build:
        scargo_build(profile)
    scargo_run(bin_path, profile, bin_params)


###############################################################################


@cli.command()
def test(
    verbose: bool = Option(False, "--verbose", "-v", help="Verbose mode."),
    profile: str = Option("Debug", "--profile", help="CMake profile to use"),
    detailed_coverage: bool = Option(
        False, help="Generate detailed coverage HTML files"
    ),
    base_dir: Optional[Path] = BASE_DIR_OPTION,
) -> None:
    """Compile and run all tests in directory `test`."""
    if base_dir:
        os.chdir(base_dir)
    scargo_test(verbose, profile, detailed_coverage)


###############################################################################


@cli.command()
def update(
    config_file_path: Optional[Path] = Option(
        None,
        "--config-file",
        "-c",
        exists=True,
        dir_okay=False,
        resolve_path=True,
        help="Path to .toml configuration file.",
    ),
    base_dir: Optional[Path] = BASE_DIR_OPTION,
) -> None:
    """Read .toml config file and generate `CMakeLists.txt`."""
    if base_dir:
        os.chdir(base_dir)
    if config_file_path is None:
        config_file_path = get_config_file_path(SCARGO_DEFAULT_CONFIG_FILE)
        if not config_file_path:
            logger.error("Config file not found.")
            sys.exit(1)
    scargo_update(config_file_path)


###############################################################################


@cli.command()
def version() -> None:
    """Get scargo version"""
    scargo_version()


###############################################################################

if __name__ == "__main__":
    cli()
