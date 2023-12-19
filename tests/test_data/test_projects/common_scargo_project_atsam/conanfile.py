#
# DO NOT EDIT THIS FILE!
# This file is generated by `scargo update`.
#
import os

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Git


class Common_scargo_project_atsamConan(ConanFile):  # type: ignore[misc, no-any-unimported]
    name = "common_scargo_project_atsam"
    version = "0.1.0"
    license = "MIT"
    description = "Project description."
    settings = "os", "compiler", "build_type", "arch"
    url = "www.hello-world.com"
    generators = "CMakeToolchain", "CMakeDeps"
    exports_sources = ["src/*", "CMakeLists.txt", "include/*", "config/*"]

    def source(self) -> None:
        self._source_atsam()

    def layout(self) -> None:
        cmake_layout(self)

    def build(self) -> None:
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self) -> None:
        copy("*.bin")
        copy("*.elf")

    def _source_atsam(self) -> None:
        import re
        from pathlib import Path

        import requests

        chip_series = "SAML10"
        dfp_outdir = Path(f"{chip_series}_DFP")
        cmsis_outdir = Path("CMSIS")
        if dfp_outdir.is_dir() and cmsis_outdir.is_dir():
            return

        self.output.info("Sourcing for atsam")
        packs_url = "http://packs.download.atmel.com"

        if not dfp_outdir.is_dir():
            packs_web_content = requests.get(packs_url).text
            match_atpack = re.search(
                f'data-link="(Atmel\\.{chip_series}\\S*\\.atpack)"',
                packs_web_content,
                re.MULTILINE | re.DOTALL,
            )
            dfp_filename = match_atpack.group(1)
            get(self, f"{packs_url}/{dfp_filename}", destination=dfp_outdir)

        if not cmsis_outdir.is_dir():
            cmsis_filename = "ARM.CMSIS.5.4.0.atpack"
            get(self, f"{packs_url}/{cmsis_filename}", destination=cmsis_outdir)
