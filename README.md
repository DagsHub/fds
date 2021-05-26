# Fast Data Science aka `fds`

[![Discord](https://img.shields.io/discord/698874030052212737)](https://discord.com/invite/9gU36Y6)
[![Tests](https://github.com/dagshub/fds/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/DAGsHub/fds/actions/workflows/test.yml)
[![PyPI](https://img.shields.io/pypi/v/fastds.svg)](https://pypi.python.org/pypi/fastds/)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)
<a href="https://twitter.com/TheRealDAGsHub" title="DAGsHub on Twitter"><img src="https://img.shields.io/twitter/follow/TheRealDAGsHub.svg?style=social"></a>

---

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

- Install `fds` using PIP `pip install fastds`
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
