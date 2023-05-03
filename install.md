Install
=======

[**<<- Back**](readme.md)

The conan-install command will run `conan install` for a specified project:

```sh
devtools conan-install --project cppql --profile cppql-test-vs2022-release
```

The `--profile` can refer to a profile stored in the Conan cache, or in the `buildtools/profiles` directory of the
specified project. Additionally, an explicit `--output-folder` can be specified to override the default folder named
`build` that is placed next to the project source folder.
