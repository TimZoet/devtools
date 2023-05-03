Export
======

[**<<- Back**](readme.md)

The export command will export all known projects to the local Conan cache. By default, the current state of each
repository is exported:

```sh
devtools export
```

It is also possible to explicitly specify the list of projects to export, as well as a branch, tag or commit to
checkout before running the export:

```sh
devtools export --projects common/v1.0.0 cppql/trunk
```
