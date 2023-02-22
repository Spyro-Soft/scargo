from conans import CMake, ConanFile, tools


class Example_projectConan(ConanFile):
    name = "example_project"
    version = "0.1.0"
    settings = "os", "compiler", "build_type", "arch"
    description = "Project description."
    url = "www.hello-world.com"
    generators = "cmake_find_package", "cmake"

    def package(self):
        self.copy("*", src="build/Debug/bin/", dst="bin", keep_path=False)
        self.copy("*", src="build/Debug/lib/", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def source(self):
        pass
