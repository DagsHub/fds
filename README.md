# Fast Data Science aka `fds`

[![CircleCI](https://circleci.com/gh/DAGsHub/fds.svg?style=svg)](https://app.circleci.com/pipelines/github/DAGsHub/fds)

`fds` is a tool for Data Scientists made by [DAGsHub](https://dagshub.com/) to version control data and code at once.

At the high level `fds` is a wrapper for Git and [DVC](https://dvc.org).  
So Data Scientists can use `fds` instead of `git` and `dvc` separately, making day-to-day work much more fluent.

## Commands Supported

| Syntax | Description                                      | Status      |
|--------|--------------------------------------------------|-------------|
| init   | Initializes git and dvc                          | Done        |
| status | Get status of git and dvc                        | Done        |
| add    | Add files to be tracked by git and dvc           | Done        |
| commit | Commit tracked files to git commit and dvc cache | Done        |

## Installation

- Install `fds` using PIP `pip install git+ssh://github.com/DAGsHub/fds.git`
- Once installed successfully, you can start using `fds`
- eg: `fds init` should trigger the init command

## Docker support

If you want to avoid pip installing `fds` and just use it directly, you can use docker:
```
docker run -v "$PWD:/repo" dagshub/fds <supported_command>
```

Example

```
➜ docker run -v "$PWD:/repo" dagshub/fds status
Untracked git files are:
.dvc/cache/
.dvc/tmp/
.gitignore
data.dvc
data/
Untracked dvc files are:
data.dvc
```

----

Made with 🐶 by [DAGsHub](https://dagshub.com/).
