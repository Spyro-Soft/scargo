from conans import CMake, ConanFile, tools


class Common_scargo_project_stm32Conan(ConanFile):
    name = "common_scargo_project_stm32"
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
        git = tools.Git(folder="third-party/stm32-cmake")
        git.clone("https://github.com/ObKo/stm32-cmake.git", "master")
