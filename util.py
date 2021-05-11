#!python
# -*- coding: utf-8 -*-

__author__ = "Tomas Zitka"
__email__ = "zitkat@kky.zcu.cz"
from pathlib import Path


def make_path(*pathargs, isdir=False, **pathkwargs):
    new_path = Path(*pathargs, **pathkwargs)
    return ensured_path(new_path, isdir=isdir)


def ensured_path(path: Path, isdir=False):
    if isdir:
        path.mkdir(parents=True, exist_ok=True)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
    return path
