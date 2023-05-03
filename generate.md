Generate
========

[**<<- Back**](readme.md)

The cmake-generate command will run `cmake -G` for a specified project:

```sh
devtools cmake-generate --project cppql
```

An explicit `--output-folder` can be specified to override the default folder named `build` that is placed next to the
project source folder.
