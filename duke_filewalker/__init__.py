import os

from .duke_filewalker import DukeFilewalker
from .keyword import Keyword
from .extraction import Pattern, Extraction

__all__ = ['DukeFilewalker', 'Keyword', 'Pattern', 'Extraction']


def walk(top, pattern, onerror=None, followlinks=False):
    try:
        names = os.listdir(top)
    except os.error as err:
        if onerror is not None:
            onerror(err)
        return

    dirs, extractions = [], []
    for name in names:
        if os.path.isdir(os.path.join(top, name)):
            if pattern.match_dir(name):
                dirs.append(name)
        else:
            extraction = pattern.extract(name)
            if extraction:
                extractions.append(extraction)

    yield extractions
    for name in dirs:
        new_path = os.path.join(top, name)
        if followlinks or not os.path.islink(new_path):
            for x in walk(new_path, pattern, onerror, followlinks):
                yield x
