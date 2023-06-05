Export Dependencies
===================

[**<<- Back**](readme.md)

The export-deps command will resolve all dependencies for a specified project and export them to the local Conan cache.
All dependencies are cloned from GitHub to a temporary folder.

```sh
devtools export-deps --project cppql --profile cppql-test-vs2022-release
```

The `--profile` can refer to a profile stored in the Conan cache, or in the `buildtools/profiles` directory of the
specified project.
