from duke_filewalker import FilePath, Extraction


def test_extraction_and_filepath():
    test_pattern = '<data_dir>/test/<run_folder>/File<filenum>.<file_type>'
    full_path = '/home/test_user/data/test/Run0001/File003.zip'
    file_dict = {'file_type': 'zip',
                 'filenum': '003'}
    dir_dict = {'data_dir': '/home/test_user/data',
                'run_folder': 'Run0001'}

    file_dict_1 = {'file_type': 'zip'}
    file_dict_2 = {'filenum': '003'}
    dir_dict_1 = {'data_dir': '/home/test_user/data'}
    dir_dict_2 = {'run_folder': 'Run0001'}


    extraction = Extraction(file_dict=file_dict,
                            dir_dict=dir_dict)
    extraction_1 = Extraction(file_dict=file_dict_1,
                            dir_dict=dir_dict_1)
    extraction_2 = Extraction(file_dict=file_dict_2,
                            dir_dict=dir_dict_2)

    filepath = FilePath(test_pattern)

    assert filepath + extraction == full_path
    assert extraction + filepath == full_path
    assert extraction + extraction + filepath == full_path
    assert extraction_1 + extraction_2 + filepath == full_path
    assert extraction_1 + filepath + extraction_2 == full_path
    assert filepath + extraction_2 + extraction_1 == full_path
    assert filepath + 'X' == test_pattern + 'X'
    assert extraction + test_pattern == full_path
    assert test_pattern + extraction == full_path
