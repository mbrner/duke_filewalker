from duke_filewalker import Pattern, Extraction
from duke_filewalker.extraction import extract


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


def test_extraction_and_filepath():
    test_pattern = '<data_dir>/test/<run_folder>/File<filenum>.<file_type>'
    full_path = '/home/user/data/test/Run0001/File003.zip'
    file_dict = {'file_type': 'zip',
                 'filenum': '003',
                 'data_dir': '/home/user/data',
                 'run_folder': 'Run0001'}

    file_dict_1 = {'file_type': 'zip',
                   'filenum': '003'}
    file_dict_2 = {'data_dir': '/home/user/data',
                   'run_folder': 'Run0001'}

    extraction = Extraction(file_dict)
    extraction_1 = Extraction(file_dict_1)
    extraction_2 = Extraction(file_dict_2)

    filepath = Pattern(test_pattern)

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

    assert filepath.extract(full_path) == file_dict
    assert filepath + filepath.extract(full_path) == full_path


if __name__ == "__main__":
    test_extraction_and_filepath()
