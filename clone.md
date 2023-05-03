Clone
=====

[**<<- Back**](readme.md)

The clone command will retrieve all known projects, placing them in the projects folder. By default, the trunk branch is
checked out. If the repository for a project already exists, no new commits are fetched and it is left in its current state:

```sh
devtools clone
```

It is also possible to explicitly specify the list of projects to retrieve, as well as a branch, tag or commit to checkout:

```sh
devtools clone --projects common/v1.0.0 cppql/trunk
```
