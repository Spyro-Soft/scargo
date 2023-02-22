from conans import CMake, ConanFile


class Example_projectTestConan(ConanFile):
    name = "example_project_test"
    version = "0.1.0"
    settings = "os", "compiler", "build_type", "arch"
    description = "Tests for example_project"
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
        self.requires("gtest/cci.20210126")
