import os

from .duke_filewalker import DukeFilewalker
from .keyword import Keyword
from .extraction import Pattern, Extraction

__all__ = ['DukeFilewalker', 'Keyword', 'Pattern', 'Extraction', 'walk']



class Walker:
    def __init__(self, top, pattern, onerror=None, followlinks=False):
        self.top = top
        self.pattern = Pattern(os.path.join(top, pattern))
        self.onerror = onerror
        self.followlinks = followlinks

    def walk(self, top=None):
        pattern = self.pattern
        onerror = self.onerror
        followlinks = self.followlinks
        if top is None:
            top = self.top
        print(top)
        try:
            names = os.listdir(top)
        except os.error as err:
            if onerror is not None:
                onerror(err)
            return

        dirs, extractions = [], []
        for name in names:
            path = os.path.join(top, name)
            if os.path.isdir(path):
                print(path)
                if pattern.match_subpath(path):
                    dirs.append(name)
                else:
                    print('Not matching')
            matching, extraction = pattern.match(path, extract=True)
            if matching:
                extractions.append(extraction)

        yield pattern, extractions
        for name in dirs:
            new_path = os.path.join(top, name)
            if followlinks or not os.path.islink(new_path):
                for x in self.walk(new_path):
                    yield x
