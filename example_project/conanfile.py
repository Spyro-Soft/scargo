from conan import CMake, ConanFile, tools  # type: ignore[import]


class Example_projectConan(ConanFile):  # type: ignore[misc, no-any-unimported]
    name = "example_project"
    version = "0.1.0"
    settings = "os", "compiler", "build_type", "arch"
    description = "Project description."
    url = "www.hello-world.com"
    generators = "cmake_find_package", "cmake"

    def package(self) -> None:
        self.copy("*", src="build/Debug/bin/", dst="bin", keep_path=False)
        self.copy("*", src="build/Debug/lib/", dst="lib", keep_path=False)

    def package_info(self) -> None:
        self.cpp_info.libs = tools.collect_libs(self)

    def build(self) -> None:
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def source(self) -> None:
        pass
