from duke_filewalker import Keyword
import fnmatch


def is_run_range(string):
    num_1, _, num_2 = string.partition('-')
    try:
        num_1 = int(num_1)
        num_2 = int(num_2)
        return True
    except ValueError:
        return False


def get_run_range(string):
    num_1, _, num_2 = string.partition('-')
    try:
        return [int(num_1), int(num_2)]
    except ValueError:
        return None


def generate_run_range(min_range=None,
                       max_range=None,
                       run_ranges=None,
                       min_length=None):
    if run_ranges is not None:
        min_range = min(run_ranges)
        max_range = max(run_ranges)
    elif min_range is None or max_range is None:
        raise AttributeError('Either min_range and max_range or run_ranges '
                             'needed!')
    if min_length is None:
        pass
    elif isinstance(min_length, int):
        if min_length > 0:
            min_range = str(min_range).zfill(min_length)
            max_range = str(max_range).zfill(min_length)
    else:
        raise ValueError('min_length has to be an positiv int or None!')
    return '{}-{}'.format(min_range, max_range)


def is_n_files(string):
    return fnmatch.fnmatch(string, '*Files')


def get_n_files(string):
    try:
        value = int(string.replace('Files', ''))
        return value
    except ValueError:
        return None


def test_keywords():
    run_number = Keyword('run_number')

    n_files = Keyword('n_files',
                      is_valid=is_n_files,
                      get_value=get_n_files)

    run_range = Keyword('run_range',
                        is_valid=is_run_range,
                        get_value=get_run_range,
                        generate=generate_run_range)

    test_run_number = 'Run00001234'
    test_n_files = '1400Files'

    test_run_range_1 = '000010-000399'
    test_run_range_2 = '10-399'
    test_run_ranges = [23, 89, 399, 102, 10]

    assert test_run_number == run_number
    assert run_number.get_value(test_run_number) == test_run_number
    get_val = run_number.get_value(test_run_number)
    assert run_number.generate(get_val) == test_run_number

    assert test_run_number != n_files
    assert test_n_files == n_files
    assert n_files.get_value(test_n_files) == 1400
    get_val = run_number.get_value(test_n_files)
    assert n_files.generate(get_val) == str(get_val)

    assert test_n_files != run_range
    assert test_run_number != run_range
    assert test_run_range_1 == run_range
    assert test_run_range_2 == run_range
    get_val_1 = run_range.get_value(test_run_range_1)
    get_val_2 = run_range.get_value(test_run_range_2)
    assert get_val_1[0] == 10
    assert get_val_1[0] == get_val_2[0]
    assert get_val_1[1] == 399
    assert get_val_1[1] == get_val_2[1]
    gen_1 = run_range.generate(min_range=get_val_1[0],
                               max_range=get_val_1[1],
                               min_length=6)
    gen_2 = run_range.generate(min_range=get_val_1[0],
                               max_range=get_val_1[1])
    gen_1_2 = run_range.generate(run_ranges=test_run_ranges,
                                 min_length=6)
    gen_2_2 = run_range.generate(run_ranges=test_run_ranges)
    assert gen_1 == test_run_range_1
    assert gen_2 == test_run_range_2
    assert gen_1_2 == test_run_range_1
    assert gen_2_2 == test_run_range_2
