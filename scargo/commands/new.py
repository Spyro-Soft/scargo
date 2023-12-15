# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Create new project"""
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

from scargo import __version__
from scargo.config import CHIP_DEFAULTS, TARGETS, ScargoTarget, Target
from scargo.config_utils import get_scargo_config_or_exit
from scargo.file_generators.cpp_gen import generate_cpp
from scargo.file_generators.toml_gen import generate_toml
from scargo.global_values import SCARGO_DEFAULT_CONFIG_FILE, SCARGO_DOCKER_ENV
from scargo.logger import get_logger
from scargo.target_helpers.atsam_helper import create_atsam_config
from scargo.target_helpers.esp32_helper import create_esp32_config
from scargo.target_helpers.stm32_helper import create_stm32_config

logger = get_logger()


def get_chip_target(chip_label: str) -> Optional[str]:
    for target in TARGETS:
        if chip_label.startswith(target):
            return target
    return None


def process_chips(chips: List[str], targets: List[ScargoTarget]) -> Dict[str, str]:
    targets_chips = {}
    unsupported_chips = []

    for chip_label in chips:
        chip_label = chip_label.lower()
        chip_target = get_chip_target(chip_label)
        if chip_target is not None:
            targets_chips[chip_target] = chip_label
        else:
            unsupported_chips.append(chip_label)

    if unsupported_chips:
        logger.error(f"Unsupported chips: {unsupported_chips}")
        sys.exit(1)

    for target in targets:
        if target.value not in targets_chips:
            targets_chips[target.value] = CHIP_DEFAULTS[target.value]

    return targets_chips


def scargo_new(
    name: str,
    bin_name: Optional[str],
    lib_name: Optional[str],
    targets: List[ScargoTarget],
    create_docker: bool,
    git: bool,
    chip: List[str],
) -> None:
    """
    Create new project

    :param str name: name of project
    :param Optional[str] bin_name: name of bin file
    :param Optional[str] lib_name: name of lib file
    :param List[Target] targets: target types for a project
    :param bool create_docker: initialize docker environment
    :param bool git: initialize git repository
    :param List[str] chip: list of chips for targets
    :return: None
    :raises FileExistsError: if project with provided name exist
    """
    if not re.match(r"[a-zA-Z][\w-]*$", name):
        logger.error(
            "Name must consist of letters, digits, dash and undescore only,"
            " and the first character must be a letter"
        )
        sys.exit(1)

    targets_chips: Dict[str, str] = process_chips(chip, targets)

    targets.extend([ScargoTarget(key) for key in targets_chips if key not in targets])
    if len(targets) == 0:
        targets = [ScargoTarget.x86]

    # If neither binary target nor library target is specified then create a
    # binary target named same as the project name.
    if not bin_name and not lib_name:
        bin_name = name  # One item tuple.

    project_dir = Path(name)
    try:
        project_dir.mkdir()
    except FileExistsError:
        logger.error("Provided project name: %s already exist.", name)
        sys.exit(1)

    build_env = get_build_env(create_docker)
    targets_ids = ", ".join([f'"{t.name}"' for t in targets])
    if len(targets_ids) > 1:
        targets_ids = f"[{targets_ids}]"

    toml_path = project_dir / SCARGO_DEFAULT_CONFIG_FILE
    generate_toml(
        toml_path,
        project_name=name,
        targets_ids=targets_ids,
        target=[Target.get_target_by_id(t.value) for t in targets],
        build_env=build_env,
        version=__version__,
        docker_image_tag=f"{name.lower()}-dev:1.0",
        lib_name=lib_name,
        bin_name=bin_name,
        atsam_config=create_atsam_config(targets_chips.get("atsam")),
        esp32_config=create_esp32_config(targets_chips.get("esp32")),
        stm32_config=create_stm32_config(targets_chips.get("stm32")),
    )

    config = get_scargo_config_or_exit(toml_path)
    generate_cpp(config)

    test_dir = project_dir / "tests"
    Path(test_dir, "mocks").mkdir(parents=True)
    Path(test_dir, "ut").mkdir(parents=True)
    Path(test_dir, "it").mkdir(parents=True)

    if git:
        subprocess.check_call("git init -q", shell=True, cwd=project_dir)
        logger.info("Initialized git repo")


def get_build_env(create_docker: bool) -> str:
    """
    Get build env
    :param bool create_docker: if create docker
    :return: build env
    """
    if create_docker:
        build_env = f"{SCARGO_DOCKER_ENV}"
    else:
        build_env = "native"
    return build_env
