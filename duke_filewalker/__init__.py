import os

from .extraction import Pattern, Extraction

__all__ = ['Pattern', 'Extraction', 'Walker']


class Walker:
    def __init__(self, pattern, followlinks=False):
        if not pattern.startswith('/'):
            top = os.getcwd()
            self.pattern = Pattern(os.path.join(top, pattern))
        else:
            self.pattern = Pattern(pattern)
        self.top = os.path.dirname(self.pattern.split('<')[0])
        self.followlinks = followlinks

    def walk(self, top=None):
        pattern = self.pattern
        followlinks = self.followlinks
        if top is None:
            top = self.top

        ext = []
        reduced_pat = None
        reduced_ext = []
        for dir_entry in os.scandir(top):
            matching, extraction = pattern.match(dir_entry.path, extract=True)
            if matching:
                ext.append(extraction)
            elif dir_entry.is_dir():
                new_pat = pattern.reduce_pattern(dir_entry.path)[0]
                if new_pat is not None:
                    matching, extraction = new_pat.match(dir_entry.path,
                                                         extract=True,
                                                         sub=True)
                    if matching:
                        reduced_ext.append(extraction)
                        if reduced_pat is None:
                            reduced_pat = new_pat
                        else:
                            assert new_pat == reduced_pat
        yield pattern, ext, reduced_pat, reduced_ext
        if reduced_pat is None:
            new_pathes = []
        else:
            new_pathes = [reduced_pat + ext_i for ext_i in reduced_ext]

        for new_path in new_pathes:
            if followlinks or not os.path.islink(new_path):
                for x in self.walk(new_path):
                    yield x
