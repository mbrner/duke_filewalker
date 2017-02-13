import os

from .extraction import Pattern, Extraction

__all__ = ['Pattern', 'Extraction', 'Walker']


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
                if pattern.match_subpath(path):
                    dirs.append(name)
            matching, extraction = pattern.match(path, extract=True)
            if matching:
                extractions.append(extraction)

        yield pattern, extractions
        for name in dirs:
            new_path = os.path.join(top, name)
            if followlinks or not os.path.islink(new_path):
                for x in self.walk(new_path):
                    yield x
