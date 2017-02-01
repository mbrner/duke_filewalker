from os import path, scandir

from .duke_filewalker import DukeFilewalker
from .keyword import Keyword
from .extraction import Pattern, Extraction

__all__ = ['DukeFilewalker', 'Keyword', 'Pattern', 'Extraction']


def walk(top, topdown=True, onerror=None, followlinks=False):
    """Directory tree generator.

    """

    dirs = []
    nondirs = []

    # We may not have read permission for top, in which case we can't
    # get a list of the files the directory contains.  os.walk
    # always suppressed the exception then, rather than blow up for a
    # minor reason when (say) a thousand readable directories are still
    # left to visit.  That logic is copied here.
    try:
        scandir_it = scandir(top)
        entries = list(scandir_it)
    except OSError as error:
        if onerror is not None:
            onerror(error)
        return

    for entry in entries:
        try:
            is_dir = entry.is_dir()
        except OSError:
            # If is_dir() raises an OSError, consider that the entry is not
            # a directory, same behaviour than os.path.isdir().
            is_dir = False

        if is_dir:
            dirs.append(entry.name)
        else:
            nondirs.append(entry.name)

        if not topdown and is_dir:
            # Bottom-up: recurse into sub-directory, but exclude symlinks to
            # directories if followlinks is False
            if followlinks:
                walk_into = True
            else:
                try:
                    is_symlink = entry.is_symlink()
                except OSError:
                    # If is_symlink() raises an OSError, consider that the
                    # entry is not a symbolic link, same behaviour than
                    # os.path.islink().
                    is_symlink = False
                walk_into = not is_symlink

            if walk_into:
                yield from walk(entry.path, topdown, onerror, followlinks)

    # Yield before recursion if going top down
    if topdown:
        yield top, dirs, nondirs

        # Recurse into sub-directories
        islink, join = path.islink, path.join
        for dirname in dirs:
            new_path = join(top, dirname)
            # Issue #23605: os.path.islink() is used instead of caching
            # entry.is_symlink() result during the loop on os.scandir() because
            # the caller can replace the directory entry during the "yield"
            # above.
            if followlinks or not islink(new_path):
                yield from walk(new_path, topdown, onerror, followlinks)
    else:
        # Yield after recursion if going bottom up
        yield top, dirs, nondirs
