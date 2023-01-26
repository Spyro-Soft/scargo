.. _arch-generators:

Generators
==========

Output of Scargo generators
---------------------------

.. uml::

   actor user

   node scargo {
       component sc_new
       component sc_update
       component toml_gen
       component conan_gen
       component cmake_gen
       component cpp_gen
   }

   folder my_project_1 {
       file scargo.toml
       file conanfile.py
       file CMakeLists.txt
       folder src {
       file CMakeLists.txt as src_cmake
       file example_project_scargo.cpp
       }
   }

   user --> scargo : executes new ...

   sc_new -down-> cpp_gen : generate_cpp
   cpp_gen -down-> example_project_scargo.cpp
   cpp_gen -down-> src_cmake

   sc_new -down-> toml_gen : generate_toml
   toml_gen -down-> scargo.toml

   sc_update -down-> conan_gen : generate_conanfile
   conan_gen -down-> conanfile.py

   sc_update -down-> cmake_gen : generate_cmake
   cmake_gen -down-> CMakeLists.txt
