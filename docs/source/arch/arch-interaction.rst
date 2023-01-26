.. _arch-interaction:

Interaction with Scargo
=======================

Scargo and other software
-------------------------

.. uml::

   !include scargo_common_seq.puml

   user -> scargo : scargo new my_project_1
   scargo -> storage : generates new project tree
   return
   return


   user -> scargo : scargo build
   alt project depends on other packages
   scargo -> conan : download dependencies
   conan -> pkg_repo : download dependencies
   return
   return
   end
   scargo -> cmake : build project
   cmake -> storage : create binary
   return
   return
   return


   user -> scargo : scargo publish
   scargo -> conan : conan upload
   conan -> storage : create package
   return
   conan -> pkg_repo : upload
   return
   return
   return


Scargo and ESP-IDF
------------------

.. uml::

   !include scargo_common_seq.puml

   user -> scargo : scargo new --arch esp32 my_project_1
   scargo -> sc_new : generate src/cpp, src/cmake
   sc_new -> storage : create src/cpp, src/cmake on disk
   return
   return
   scargo -> sc_update : generate top level cmake
   sc_update -> storage: create top level cmake on disk
   return
   return
   return

   user -> scargo : scargo build
   scargo -> sc_build : execute build
   sc_build -> esp_idf : idf.py buildall (subprocess call)
   esp_idf -> storage : create binary
   return
   return
   return
   return
