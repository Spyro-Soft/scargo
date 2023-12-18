# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import toml
from pydantic import BaseModel, Extra, Field, root_validator

from scargo.global_values import SCARGO_DEFAULT_BUILD_ENV, SCARGO_DOCKER_ENV


class ScargoTarget(Enum):
    atsam = "atsam"
    esp32 = "esp32"
    stm32 = "stm32"
    x86 = "x86"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return self.value == other
        if isinstance(other, ScargoTarget):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return super().__hash__()


CHIP_DEFAULTS = {
    "x86": "",
    "esp32": "esp32",
    "atsam": "ATSAML10E16A",
    "stm32": "STM32L496AG",
}

ESP32_DEFAULT_PARTITIONS = [
    "nvs,      data, nvs,     0x9000,  0x4000,",
    "otadata,  data, ota,     0xd000,  0x2000,",
    "phy_init, data, phy,     0xf000,  0x1000,",
    "ota_0,    app,  ota_0,   0x10000, 0x180000,",
    "ota_1,    app,  ota_1,   0x190000,0x180000,",
    "spiffs,   data, spiffs,  0x310000,0x6000,",
]


class ConfigError(Exception):
    pass


class Config(BaseModel):
    project: "ProjectConfig"
    profiles: Dict[str, "ProfileConfig"] = Field(..., alias="profile")
    check: "ChecksConfig"
    fix: "FixesConfig" = Field(
        default_factory=lambda: FixesConfig()  # pylint: disable=unnecessary-lambda
    )
    doc: "DocConfig" = Field(
        default_factory=lambda: DocConfig()  # pylint: disable=unnecessary-lambda
    )
    tests: "TestConfig"
    dependencies: "Dependencies"
    conan: "ConanConfig"
    atsam: Optional["ATSAMConfig"]
    stm32: Optional["Stm32Config"]
    esp32: Optional["Esp32Config"]
    scargo: "ScargoConfig" = Field(
        default_factory=lambda: ScargoConfig()  # pylint: disable=unnecessary-lambda
    )
    docker_compose: "DockerComposeConfig" = Field(
        default_factory=lambda: DockerComposeConfig(),  # pylint: disable=unnecessary-lambda
        alias="docker-compose",
    )
    project_root: Path

    @property
    def source_dir_path(self) -> Path:
        if self.project.is_esp32():
            # Backwards compatibility for main dir
            main_dir = self.project_root / COMPATIBILITY_ESP32_SRC_DIR
            if main_dir.is_dir():
                return main_dir
        return self.project_root / DEFAULT_SRC_DIR

    @property
    def include_dir_path(self) -> Path:
        return self.source_dir_path / DEFAULT_INCLUDE_DIR

    def get_atsam_config(self) -> "ATSAMConfig":
        if not self.atsam:
            raise ConfigError("No [atsam] section in config")
        return self.atsam

    def get_stm32_config(self) -> "Stm32Config":
        if not self.stm32:
            raise ConfigError("No [stm32] section in config")
        return self.stm32

    def get_esp32_config(self) -> "Esp32Config":
        if not self.esp32:
            raise ConfigError("No [esp32] section in config")
        return self.esp32

    @root_validator
    def validate_special_configs(  # pylint: disable=no-self-argument
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        if "project" in values:
            target_id = values["project"].target_id
            targets_for_validation = [
                ScargoTarget.stm32.value,
                ScargoTarget.esp32.value,
                ScargoTarget.atsam.value,
            ]
            for target in targets_for_validation:
                if target in target_id and not values.get(target):
                    raise ConfigError(f"No [{target}] section in config")

        # Set default value of cmake_build_type - Debug for non-stanard profiles,
        # If profile is on standard_profiles list, use it's name instead
        standard_profiles: List[str] = [
            "Debug",
            "Release",
            "RelWithDebInfo",
            "MinSizeRel",
        ]
        if "profiles" in values:
            for name, profile in values["profiles"].items():
                if profile.cmake_build_type is None:
                    if name in standard_profiles:
                        profile.cmake_build_type = name
                    else:
                        profile.cmake_build_type = "Debug"
        return values


class ProjectConfig(BaseModel):
    name: str
    version: str
    description: Optional[str]
    homepage_url: Optional[str] = Field(default=None, alias="homepage-url")

    bin_name: Optional[str]
    lib_name: Optional[str]
    target_id: Union[str, List[str]] = Field(..., alias="target")
    build_env: str = Field(SCARGO_DEFAULT_BUILD_ENV, alias="build-env")
    docker_file: Path = Field(..., alias="docker-file")
    docker_image_tag: str = Field(..., alias="docker-image-tag")
    in_repo_conan_cache: bool = Field(..., alias="in-repo-conan-cache")

    cc: Optional[str] = None
    cxx: Optional[str] = None
    cxxstandard: str

    cflags: str
    cxxflags: str

    max_build_jobs: Optional[int] = Field(default=None, alias="max-build-jobs")
    cmake_variables: Dict[str, str] = Field(default={}, alias="cmake-variables")

    @property
    def target(self) -> List["Target"]:
        if isinstance(self.target_id, str):
            return Target.get_targets_by_id([self.target_id])
        return Target.get_targets_by_id(self.target_id)

    @property
    def default_target(self) -> "Target":
        if isinstance(self.target_id, str):
            return Target.get_target_by_id(self.target_id)
        return Target.get_target_by_id(self.target_id[0])

    def is_docker_buildenv(self) -> bool:
        return self.build_env == SCARGO_DOCKER_ENV

    def is_x86(self) -> bool:
        return "x86" in self.target_id

    def is_stm32(self) -> bool:
        return "stm32" in self.target_id

    def is_esp32(self) -> bool:
        return "esp32" in self.target_id

    def is_atsam(self) -> bool:
        return "atsam" in self.target_id

    def is_multitarget(self) -> bool:
        return isinstance(self.target_id, list) and len(self.target_id) > 1


class Target(BaseModel):
    id: str
    elf_file_extension: str
    cc: Optional[str] = None
    cxx: Optional[str] = None

    def get_profile_build_dir(self, profile: str = "Debug") -> str:
        return f"build/{self.id}/{profile}"

    def get_conan_profile_name(self, profile: str = "Debug") -> str:
        return f"{self.id}_{profile}"

    def get_bin_dir_path(self, profile: str = "Debug") -> str:
        build_dir = self.get_profile_build_dir(profile)
        if self.id == ScargoTarget.esp32:
            return build_dir
        return f"{build_dir}/bin"

    def get_bin_path(self, bin_name: str, profile: str = "Debug") -> str:
        bin_dir = self.get_bin_dir_path(profile)
        return f"{bin_dir}/{bin_name}{self.elf_file_extension}"

    @classmethod
    def get_target_by_id(cls, target_id: str) -> "Target":
        return TARGETS[target_id]

    @classmethod
    def get_targets_by_id(cls, target_ids: List[str]) -> List["Target"]:
        return [TARGETS[id] for id in target_ids]


DEFAULT_SRC_DIR = "src"
COMPATIBILITY_ESP32_SRC_DIR = "main"
DEFAULT_INCLUDE_DIR = "include"
TARGETS = {
    ScargoTarget.x86.value: Target(
        id=ScargoTarget.x86.value,
        elf_file_extension="",
        cc="gcc",
        cxx="g++",
    ),
    ScargoTarget.stm32.value: Target(
        id=ScargoTarget.stm32.value, elf_file_extension=".elf"
    ),
    ScargoTarget.esp32.value: Target(
        id=ScargoTarget.esp32.value, elf_file_extension=".elf"
    ),
    ScargoTarget.atsam.value: Target(
        id=ScargoTarget.atsam.value, elf_file_extension=""
    ),
}


class ProfileConfig(BaseModel, extra=Extra.allow):
    cflags: Optional[str]
    cxxflags: Optional[str]
    cc: Optional[str] = None
    cxx: Optional[str] = None
    cmake_build_type: Optional[str] = Field(default=None, alias="cmake-build-type")

    @property
    def extras(self) -> Dict[str, Any]:
        return {
            key: value
            for key, value in dict(self).items()
            if key not in self.__fields__
        }


class ChecksConfig(BaseModel):
    exclude: List[str]
    pragma: "CheckConfig"
    copyright: "CheckConfig"
    todo: "TodoCheckConfig"
    clang_format: "CheckConfig" = Field(..., alias="clang-format")
    clang_tidy: "CheckConfig" = Field(..., alias="clang-tidy")
    cyclomatic: "CheckConfig"


class FixesConfig(BaseModel):
    copyright: "FixConfig" = Field(
        default_factory=lambda: FixConfig()  # pylint: disable=unnecessary-lambda
    )


class CheckConfig(BaseModel):
    description: Optional[str] = None
    exclude: List[str] = Field(default_factory=list)


class FixConfig(BaseModel):
    description: Optional[str] = None


class TodoCheckConfig(CheckConfig):
    keywords: List[str] = Field(default_factory=list)


class DocConfig(BaseModel):
    exclude: List[str] = Field(default_factory=list)


class TestConfig(BaseModel, extra=Extra.allow):
    cc: str
    cxx: str

    cflags: str
    cxxflags: str

    gcov_executable: str = Field(..., alias="gcov-executable")

    @property
    def extras(self) -> Dict[str, Any]:
        return {
            key: value
            for key, value in dict(self).items()
            if key not in self.__fields__
        }


class Dependencies(BaseModel):
    general: List[str] = Field(default_factory=list)
    build: List[str] = Field(default_factory=list)
    tool: List[str] = Field(default_factory=list)
    test: List[str] = Field(default_factory=list)


class ConanConfig(BaseModel):
    repo: Dict[str, str]  # name to url mapping


class Stm32Config(BaseModel):
    chip: str = Field(default=CHIP_DEFAULTS.get("stm32"))
    flash_start: int = Field(default=0x08000000, alias="flash-start")


class ATSAMConfig(BaseModel):
    chip: str = Field(default=CHIP_DEFAULTS.get("atsam"))
    cpu: str = Field()

    @property
    def chip_series(self) -> str:
        return self.chip[2:8].upper()


class Esp32Config(BaseModel):
    chip: str = Field(default=CHIP_DEFAULTS.get("esp32"))
    extra_component_dirs: List[Path] = Field(default=["src"])
    partitions: List[str] = Field(default=ESP32_DEFAULT_PARTITIONS)


class ScargoConfig(BaseModel):
    console_log_level: str = Field(default="INFO", alias="console-log-level")
    file_log_level: str = Field(default="WARNING", alias="file-log-level")
    update_exclude: List[str] = Field(alias="update-exclude", default_factory=list)
    version: Optional[str] = None


class DockerComposeConfig(BaseModel):
    ports: List[str] = Field(default_factory=list)


Config.update_forward_refs()
ProjectConfig.update_forward_refs()
ChecksConfig.update_forward_refs()
FixesConfig.update_forward_refs()
FixConfig.update_forward_refs()
Stm32Config.update_forward_refs()
Esp32Config.update_forward_refs()


def parse_config(config_file_path: Path) -> Config:
    config_obj = toml.load(config_file_path)
    config_obj["project_root"] = config_file_path.parent.absolute()
    config: Config = Config.parse_obj(config_obj)
    return config
