from conans import CMake, ConanFile, tools


class Esp32projectTestConan(ConanFile):
    name = "esp32project_test"
    version = "0.1.0"
    settings = "os", "compiler", "build_type", "arch"
    description = "Tests for esp32project"
    url = "www.hello-world.com"
    generators = "cmake_find_package", "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        target_test = "RUN_TESTS" if self.settings.os == "Windows" else "test"
        self.cmake.build(target=target_test)

    def requirements(self):
        self.requires("gtest/1.12.1")
