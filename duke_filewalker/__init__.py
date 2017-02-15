import os

from .extraction import Pattern, Extraction

__all__ = ['Pattern', 'Extraction', 'Walker']


class Walker:
    def __init__(self, pattern, onerror=None, followlinks=False):
        if not pattern.startswith('/'):
            top = os.getcwd()
            self.pattern = Pattern(os.path.join(top, pattern))
        else:
            self.pattern = Pattern(pattern)
        self.top = os.path.dirname(self.pattern.split('<')[0])
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

        ext = []
        reduced_pat = []
        reduced_ext = []
        for name in names:
            path = os.path.join(top, name)
            matching, extraction = pattern.match(path, extract=True)
            if matching:
                ext.append(extraction)
            else:
                matching, reduced_pattern, extraction = pattern.match_subpath(
                    path,
                    extract=True)
                if matching:
                    reduced_pat.append(reduced_pattern)
                    reduced_ext.append(extraction)

        yield pattern, ext, reduced_pat, reduced_ext
        for new_path in [pat_i + ext_i for pat_i , ext_i in zip(reduced_pat,
                reduced_ext)]:
            if followlinks or not os.path.islink(new_path):
                for x in self.walk(new_path):
                    yield x
