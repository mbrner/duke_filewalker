import os

from .duke_filewalker import DukeFilewalker
from .keyword import Keyword
from .extraction import Pattern, Extraction

__all__ = ['DukeFilewalker', 'Keyword', 'Pattern', 'Extraction']


def walk(top, topdown=True, onerror=None, followlinks=False):
    try:
        names = os.listdir(top)
    except os.error as err:
        if onerror is not None:
            onerror(err)
        return

    dirs, nondirs = [], []
    for name in names:
        if os.path.isdir(os.path.join(top, name)):
            dirs.append(name)
        else:
            nondirs.append(name)

    if topdown:
        yield top, dirs, nondirs
    for name in dirs:
        new_path = os.path.join(top, name)
        if followlinks or not os.path.islink(new_path):
            for x in walk(new_path, topdown, onerror, followlinks):
                yield x
    if not topdown:
        yield top, dirs, nondirs
