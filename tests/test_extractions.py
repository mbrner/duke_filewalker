from duke_filewalker import Pattern, Extraction
from duke_filewalker.extraction import extract, get_keywords, Keyword


def test_extract():
    assert extract(string='/a/c/a/b/',
                   pattern='/a/<1>/<2>/b/') == {'1': 'c', '2': 'a'}

    assert extract(string='/a/c/a/b/',
                   pattern='/<1>/<2>/a/b/') == {'1': 'a', '2': 'c'}

    assert extract(string='/a/c/a/b/',
                   pattern='/<1>/<2>/<3>/b/') == {'1': 'a', '2': 'c', '3': 'a'}

    assert extract(string='/a/c/a/b/',
                   pattern='/<1>/<2>/<3>/<4>/'
                   ) == {'1': 'a', '2': 'c', '3': 'a', '4': 'b'}

    assert extract(string='/a/c/',
                   pattern='/<1>/<2>/<3>/<4>/'
                   ) == {'1': 'a', '2': 'c'}


def test_extraction_and_filepath():
    pattern_1 = '/home/user/data/test/<run_folder>/File<filenum>.<file_type>'
    pattern_2 = '<data_dir::0>/test/<run_folder>/File<filenum>.<file_type>'
    pattern_3 = '/home/user/data/test/<run_folder>/File<filenum>.zip'
    pattern_4 = '<data_dir::0>/test/<run_folder>/File<filenum>.zip'
    pattern_5 = '<data_dir::0>/test/<run_folder::1>/File<filenum>.<file_type>'

    full_path = '/home/user/data/test/Run0001/File003.zip'
    full_path_2 = '/home/user/data/test/Run0001/SubFolder/File003.zip'
    partially_path = '/home/user/data/test/Run0001/'
    partially_path_2 = '/home/user/data/test/Run0001/SubFolder'

    wrong_path = '/home/user/data/test/Run0001/log.txt'
    full_dict = {'file_type': 'zip',
                 'filenum': '003',
                 'data_dir': '/home/user/data',
                 'run_folder': 'Run0001'}

    file_dict_1 = {'file_type': 'zip',
                   'filenum': '003'}
    file_dict_2 = {'data_dir': '/home/user/data',
                   'run_folder': 'Run0001'}

    assert get_keywords(pattern_1) == ['run_folder',
                                       'filenum',
                                       'file_type']
    assert get_keywords(pattern_2) == ['data_dir',
                                       'run_folder',
                                       'filenum',
                                       'file_type']
    for test_pattern in [pattern_1,
                         pattern_2,
                         pattern_3,
                         pattern_4,
                         pattern_5]:
        filepath = Pattern(test_pattern)
        extraction = Extraction(full_dict)
        extraction_1 = Extraction(file_dict_1)
        extraction_2 = Extraction(file_dict_2)

        file_dict = {}
        kws = get_keywords(test_pattern)
        for kw in kws:
            file_dict[kw] = full_dict[kw]
        assert filepath + extraction == full_path
        assert extraction + filepath == full_path
        assert extraction + extraction + filepath == full_path
        assert extraction_1 + extraction_2 + filepath == full_path
        assert extraction_1 + filepath + extraction_2 == full_path
        assert filepath + extraction_2 + extraction_1 == full_path
        assert filepath + 'X' == test_pattern + 'X'
        assert extraction + test_pattern == full_path
        assert test_pattern + extraction == full_path

        assert filepath.match(full_path)
        filepath_extraction_1 = filepath + extraction_1
        assert filepath_extraction_1.match(full_path)
        filepath_extraction_2 = filepath_extraction_1 + extraction_2
        assert filepath_extraction_2.match(full_path)
        assert (filepath + extraction_1 + extraction_2).match(full_path)
        assert not filepath.match(wrong_path)
        assert filepath.extract(full_path) == file_dict
        assert filepath + filepath.extract(full_path) == full_path
        assert filepath.match(full_path)
        assert not filepath.match(full_path_2)
        assert not filepath.match(partially_path)
        assert not filepath.match_subpath(partially_path_2)
        assert not filepath.match_subpath(wrong_path)


def test_keyword():
    name = 'data_dir'
    wrong_value_1 = 'home/user/test/data'
    wrong_value_2 = '/home/user/test/data/'
    wrong_value_3 = 'home/user/test/data/'
    wrong_value_4 = '/home/user/test/data'
    correct_value_1 = 'home/user/test'
    correct_value_2 = '/home/user/test/'
    correct_value_3 = 'home/user/test/'
    correct_value_4 = '/home/user/test'

    test_keyword = Keyword('data_dir::0')
    test_keyword_depth = Keyword('data_dir::3')

    assert test_keyword == name
    assert test_keyword_depth == name
    assert test_keyword_depth == test_keyword
    assert str(test_keyword) == name
    assert str(test_keyword_depth) == name

    assert test_keyword.match(correct_value_1)
    assert test_keyword.match(correct_value_2)
    assert test_keyword.match(correct_value_3)
    assert test_keyword.match(correct_value_4)
    assert test_keyword_depth.match(correct_value_1)
    assert test_keyword_depth.match(correct_value_2)
    assert test_keyword_depth.match(correct_value_3)
    assert test_keyword_depth.match(correct_value_4)

    assert test_keyword.match(wrong_value_1)
    assert test_keyword.match(wrong_value_2)
    assert test_keyword.match(wrong_value_3)
    assert test_keyword.match(wrong_value_4)
    assert not test_keyword_depth.match(wrong_value_1)
    assert not test_keyword_depth.match(wrong_value_2)
    assert not test_keyword_depth.match(wrong_value_3)
    assert not test_keyword_depth.match(wrong_value_4)

if __name__ == "__main__":
    test_keyword()
    test_extraction_and_filepath()
