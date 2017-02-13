import os
import contextlib
import shutil

import duke_filewalker


def touch(file_path):
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(file_path, 'a'):
        os.utime(file_path, None)
    return file_path


@contextlib.contextmanager
def dummy_files(top, file_list):
    if os.path.exists(top):
        raise ValueError('\'top\' ({}) already exists!'.format(top))
    full_pathes = []
    top = os.path.abspath(top)
    for file_i in file_list:
        if file_i.startswith('/'):
            file_i = file_i[1:]
        file_i = os.path.join(top, file_i)
        full_pathes.append(touch(file_i))
    yield full_pathes
    shutil.rmtree(top)


def test_walk():
    test_structure = []
    test_structure.append('a/c/a/b/f_correct.txt')
    test_structure.append('a/c/a/f_correct.txt')
    test_structure.append('a/c/b/f_correct.txt')
    test_structure.append('a/a/b/f_correct.txt')
    test_structure.append('a/b/f_correct.txt')
    test_structure.append('a/c/a/b/f_wrong.txt')
    test_structure.append('a/c/a/f_wrong.txt')
    test_structure.append('a/c/b/f_wrong.txt')
    test_structure.append('a/a/b/f_wrong.txt')
    test_structure.append('a/c/f_wrong.txt')

    top = os.path.dirname(os.path.dirname(duke_filewalker.__file__))
    top = os.path.join(top, 'tests/test_structure')

    with dummy_files(top, test_structure):
        pattern = '<folders::0>/f_<file_name>.txt'
        walker = duke_filewalker.Walker(top, pattern)
        found = []
        for pat, ext in walker.walk():
            for ext_i in ext:
                found.append(pat + ext_i)
        assert len(found) == 10

        pattern_correct = 'a/<folders::0>/f_correct.txt'
        walker_correct = duke_filewalker.Walker(top, pattern_correct)
        found_correct = []
        for pat, ext in walker_correct.walk():
            for ext_i in ext:
                found_correct.append(pat + ext_i)
        assert len(found_correct) == 5

        pattern_wrong = 'a/<folders::0>/f_wrong.txt'
        walker_wrong = duke_filewalker.Walker(top, pattern_wrong)
        found_wrong = []
        for pat, ext in walker_wrong.walk():
            for ext_i in ext:
                found_wrong.append(pat + ext_i)
        assert len(found_wrong) == 5

        pattern_correct = 'a/<folders::1>/f_correct.txt'
        walker_correct = duke_filewalker.Walker(top, pattern_correct)
        found_correct = []
        for pat, ext in walker_correct.walk():
            for ext_i in ext:
                found_correct.append(pat + ext_i)
        assert len(found_correct) == 1

        pattern_wrong = 'a/<folders::1>/f_wrong.txt'
        walker_wrong = duke_filewalker.Walker(top, pattern_wrong)
        found_wrong = []
        for pat, ext in walker_wrong.walk():
            for ext_i in ext:
                found_wrong.append(pat + ext_i)
        assert len(found_wrong) == 1

        pattern_correct = 'a/<folders::2>/f_correct.txt'
        walker_correct = duke_filewalker.Walker(top, pattern_correct)
        found_correct = []
        for pat, ext in walker_correct.walk():
            for ext_i in ext:
                found_correct.append(pat + ext_i)
        assert len(found_correct) == 3

        pattern_wrong = 'a/<folders::2>/f_wrong.txt'
        walker_wrong = duke_filewalker.Walker(top, pattern_wrong)
        found_wrong = []
        for pat, ext in walker_wrong.walk():
            for ext_i in ext:
                found_wrong.append(pat + ext_i)
        assert len(found_wrong) == 3

        pattern_correct = 'a/<folders::1>/<folders_2::1>/f_correct.txt'
        walker_correct = duke_filewalker.Walker(top, pattern_correct)
        found_correct = []
        for pat, ext in walker_correct.walk():
            for ext_i in ext:
                found_correct.append(pat + ext_i)
        assert len(found_correct) == 3


if __name__ == '__main__':
    test_walk()
