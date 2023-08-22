from conans import CMake, ConanFile  # type: ignore[import]


class Esp32projectTestConan(ConanFile):  # type: ignore[misc, no-any-unimported]
    name = "esp32project_test"
    version = "0.1.0"
    settings = "os", "compiler", "build_type", "arch"
    description = "Tests for esp32project"
    url = "www.hello-world.com"
    generators = "cmake_find_package", "cmake"

    def build(self) -> None:
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self) -> None:
        target_test = "RUN_TESTS" if self.settings.os == "Windows" else "test"  # type: ignore[attr-defined]
        self.cmake.build(target=target_test)

    def requirements(self) -> None:
        self.requires("gtest/1.12.1")
