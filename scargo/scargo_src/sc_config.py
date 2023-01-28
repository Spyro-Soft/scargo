# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import toml
from pydantic import BaseModel, Extra, Field

from scargo.scargo_src.global_values import SCARGO_DEFAULT_BUILD_ENV


class Config(BaseModel):
    project: "ProjectConfig"
    profiles: Dict[str, "ProfileConfig"] = Field(..., alias="profile")
    check: "ChecksConfig"
    tests: "TestConfig"
    dependencies: "Dependencies"
    conan: "ConanConfig"
    stm32: Optional["Stm32Config"]
    esp32: Optional["Esp32Config"]
    scargo: "ScargoConfig" = Field(default_factory=lambda: ScargoConfig())


class ProjectConfig(BaseModel):
    name: str
    version: str
    description: Optional[str]
    homepage_url: Optional[str] = Field(None, alias="homepage-url")

    bin_name: Optional[str]
    lib_name: Optional[str]
    target_id: str = Field(..., alias="target")
    build_env: str = Field(SCARGO_DEFAULT_BUILD_ENV, alias="build-env")
    docker_file: Path = Field(..., alias="docker-file")
    docker_image_tag: str = Field(..., alias="docker-image-tag")
    in_repo_conan_cache: bool = Field(..., alias="in-repo-conan-cache")

    cc: str
    cxx: str
    cxxstandard: str

    cflags: str
    cxxflags: str

    @property
    def target(self) -> "Target":
        return Target.get_target_by_id(self.target_id)


class Target(BaseModel):
    id: str
    family: str
    source_dir: str
    cc: str
    cxx: str

    @classmethod
    def get_target_by_id(cls, target_id):
        return TARGETS[target_id]


ARM_CC = "arm-none-eabi-gcc"
ARM_CXX = "arm-none-eabi-g++"

TARGETS = {
    "x86": Target(id="x86", family="x86", source_dir="src", cc="gcc", cxx="g++"),
    "stm32": Target(
        id="stm32", family="stm32", source_dir="src", cc=ARM_CC, cxx=ARM_CXX
    ),
    "esp32": Target(
        id="esp32", family="esp32", source_dir="main", cc=ARM_CC, cxx=ARM_CXX
    ),
    "esp32s2": Target(
        id="esp32s2", family="esp32", source_dir="main", cc=ARM_CC, cxx=ARM_CXX
    ),
    "esp32s3": Target(
        id="esp32s3", family="esp32", source_dir="main", cc=ARM_CC, cxx=ARM_CXX
    ),
    "esp32c2": Target(
        id="esp32c2", family="esp32", source_dir="main", cc=ARM_CC, cxx=ARM_CXX
    ),
    "esp32c3": Target(
        id="esp32c3", family="esp32", source_dir="main", cc=ARM_CC, cxx=ARM_CXX
    ),
}


# for typer
ScargoTargets = Enum(
    "ScargoTargets", {target.id: target.id for target in TARGETS.values()}
)


class ProfileConfig(BaseModel, extra=Extra.allow):
    cflags: Optional[str]
    cxxflags: Optional[str]

    @property
    def extras(self):
        return {
            key: value
            for key, value in dict(self).items()
            if key not in self.__fields__
        }


class ChecksConfig(BaseModel):
    exclude: List[str]
    pragma: "CheckConfig"
    copyright: "CheckConfig"
    todo: "CheckConfig"
    clang_format: "CheckConfig" = Field(..., alias="clang-format")
    clang_tidy: "CheckConfig" = Field(..., alias="clang-tidy")
    cyclomatic: "CheckConfig"


class CheckConfig(BaseModel):
    description: Optional[str]
    exclude: List[str] = Field(default_factory=list)


class TestConfig(BaseModel):
    cc: str
    cxx: str

    cflags: str
    cxxflags: str

    gcov_executable: str = Field(..., alias="gcov-executable")


class Dependencies(BaseModel):
    general: List[str] = Field(default_factory=list)
    build: List[str] = Field(default_factory=list)
    tool: List[str] = Field(default_factory=list)
    test: List[str] = Field(default_factory=list)


class ConanConfig(BaseModel):
    repo: Dict[str, str]  # name to url mapping


class Stm32Config(BaseModel):
    chip: str
    flash_start: int = Field(alias="flash-start")


class Esp32Config(BaseModel):
    extra_component_dirs: List[Path] = Field(default_factory=list)
    partitions: List[str] = Field(default_factory=list)


class ScargoConfig(BaseModel):
    console_log_level: str = Field("INFO", alias="console-log-level")
    file_log_level: str = Field("WARNING", alias="file-log-level")
    update_exclude: List[str] = Field(alias="update-exclude", default_factory=list)
    version: Optional[str]


Config.update_forward_refs()
ProjectConfig.update_forward_refs()
ChecksConfig.update_forward_refs()
Stm32Config.update_forward_refs()
Esp32Config.update_forward_refs()


def parse_config(config_file_path: Path) -> Config:
    return Config.parse_obj(toml.load(config_file_path))
