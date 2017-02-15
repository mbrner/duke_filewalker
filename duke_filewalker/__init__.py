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
        reduced_pat = None
        reduced_ext = []
        for name in names:
            path = os.path.join(top, name)
            matching, extraction = pattern.match(path, extract=True)
            if matching:
                ext.append(extraction)
            else:
                if reduced_pat is None:
                    reduced_pat, _ = pattern.reduce_pattern(path)
                else:
                    assert reduced_pat == pattern.reduce_pattern(path)[0]
                if reduced_pat is not None:
                    matching, extraction = reduced_pat.match(path,
                                                             extract=True,
                                                             sub=True)
                    if matching:
                        reduced_ext.append(extraction)

        yield pattern, ext, reduced_pat, reduced_ext
        if reduced_pat is None:
            new_pathes = []
        else:
            new_pathes = [reduced_pat + ext_i for ext_i in reduced_ext]

        for new_path in new_pathes:
            if followlinks or not os.path.islink(new_path):
                for x in self.walk(new_path):
                    yield x
