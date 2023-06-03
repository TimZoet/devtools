Readme
======

This repository contains instructions and Python scripts containing high level functionality to quickly setup a
development environment. There are a number of commands you can use. Each is described on its own page. An overview:

Environment Setup
-----------------

* [**setup**](setup.md) Prepares a development environment.
* [**python-packages**](packages.md) Installs required Python packages.
* [**clone**](clone.md) Clones all known or explicitly specified projects.

Conan Cache
-----------

* [**export**](export.md) Exports packages to the local Conan cache.
* [**export-deps**](export_deps.md) Automatically resolves all required packages for a single project and exports them
to the local Conan cache.
* [**clear-cache**](clear_cache.md) Removes all known projects from the local Conan cache.

Project Setup
-------------

* [**conan-install**](install.md) Runs the `conan install` command for a single project.
* [**cmake-generate**](generate.md) Runs the `cmake generate` command for a single project.

Utils
-----

* [**clang-format**](clang_format.md) Runs `clang-format` on all files in a single project.
