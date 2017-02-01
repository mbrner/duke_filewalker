from __future__ import division, absolute_import
from __future__ import with_statement, print_function
import logging
import os
import difflib
import re
import fnmatch
from .keyword import Keyword
from .extraction import Extraction

logger = logging.getLogger('DukeFileWalker')


class DukeFilewalker:
    def __init__(self):
        self.kw_file = {}
        self.kw_dir = {}

    def __call__(self, kw, *args, **kwargs):
        if kw in self.kw_dir:
            gen_dir = self.kw_dir[kw](*args, **kwargs)
        else:
            gen_dir = None
        if kw in self.kw_file:
            gen_file = self.kw_file[kw](*args, **kwargs)
        else:
            gen_file = None
        return [gen_dir, gen_file]

    def register_kw(self,
                    name,
                    is_valid_func=None,
                    get_value_func=None,
                    generation_func=None,
                    for_='both'):
        kw = Keyword(name=name,
                     is_valid=is_valid_func,
                     get_value=get_value_func,
                     generate=generation_func)
        if for_.lower() == 'both' or for_.lower() == 'file':
            self.kw_file[name.lower()] = kw

        if for_.lower() == 'both' or for_.lower() == 'dir':
            self.kw_dir[name.lower()] = kw
        logger.debug('Registered Keyword {}!'.format(repr(kw)))

    def extract(self,
                pathes,
                pattern,
                only_registered=True,
                convert=True,
                ignore_unconvertables=True):
        logger.debug('Extracting!')
        if isinstance(pathes, str):
            pathes = [pathes]
        filename_pattern = os.path.basename(pattern)
        directory_pattern = os.path.dirname(pattern)

        kw_file = re.findall(r'\<(.*?)\>', filename_pattern)
        if len(kw_file) > 0:
            filename_diff = filename_pattern
            for kw in kw_file:
                replace_str = '<{}>'.format(kw)
                filename_diff = filename_diff.replace(replace_str, '*')
        else:
            filename_diff = None
        if only_registered:
            if any([kw not in self.kw_file for kw in kw_file]):
                kws = [kw for kw in kw_file if kw not in self.kw_file]
                raise ValueError('File part of the pattern has '
                                 'unregistered keyword(s) {}!'.format(kws))
        logger.debug('\t File:\t\tKeywords: {}\n\t\tDiffpattern: {}'.format(
            ', '.join(kw_file), filename_diff))

        kw_dir = re.findall(r'\<(.*?)\>', directory_pattern)
        if len(kw_dir) > 0:
            directory_diff = directory_pattern
            for kw in kw_dir:
                replace_str = '<{}>'.format(kw)
                directory_diff = directory_diff.replace(replace_str, '*')
        else:
            directory_diff = None
        if only_registered:
            if any([kw not in self.kw_dir for kw in kw_dir]):
                kws = [kw for kw in kw_dir if kw not in self.kw_dir]
                raise ValueError('Directory part of the pattern has '
                                 'unregistered keyword(s) {}!'.format(kws))
        logger.debug('\t Path:\t\tKeywords: {}\n\t\tDiffpattern: {}'.format(
            ', '.join(kw_dir), directory_diff))

        filenames = map(os.path.basename, pathes)
        directories = map(os.path.dirname, pathes)
        extractions = []
        for dir_i, name_i in zip(directories, filenames):
            extraction_dir = None
            if directory_diff is not None:
                if fnmatch.fnmatch(dir_i, directory_diff):
                    extraction_dir = self._extract_single_(dir_i,
                                                           directory_diff,
                                                           kw_dir)
                    if convert:
                        for kw in extraction_dir.keys():
                            string = extraction_dir[kw]
                            value = self.kw_dir[kw](string)
                            if value is None:
                                if not ignore_unconvertables:
                                    raise ValueError(
                                        '"{}" unconvertable to  "{}"'.format(
                                            string, kw))
                            else:
                                extraction_dir[kw] = value

            extraction_file = None
            if filename_diff is not None:
                print(name_i, filename_diff)
                if fnmatch.fnmatch(name_i, filename_diff):
                    extraction_file = self._extract_single_(name_i,
                                                            filename_diff,
                                                            kw_file)
                    if convert:
                        for kw in extraction_file.keys():
                            string = extraction_file[kw]
                            value = self.kw_file[kw](string)
                            if value is None:
                                if not ignore_unconvertables:
                                    raise ValueError(
                                        '"{}" unconvertable to  "{}"'.format(
                                            string, kw))
                            else:
                                extraction_file[kw] = value
            extractions.append(Extraction(dir_dict=extraction_dir,
                                          file_dict=extraction_file))
        return extractions

    def _extract_single_(self, inpath, pattern_diff, keywords):
        extraction = {}
        pointer = 0
        match = ''
        in_ = False
        for c, _, s in difflib.ndiff(pattern_diff, inpath):
            if c == '-' and s == '*':
                in_ = True
            elif c == '-' and s != '*':
                break
            elif in_ and c == '+':
                match += s
            elif in_ and c == ' ':
                in_ = False
                if len(match) == 0:
                    raise AttributeError(
                        'Unexpected str found: {} {}'.format(pattern_diff,
                                                             inpath))
                extraction[keywords[pointer]] = match
                match = ''
                pointer += 1
        if in_:
            if len(match) == 0:
                pass
            else:
                extraction[keywords[pointer]] = match
        return extraction

    def replace(extractions, pattern, complete=False):

        for extraction in extractions:
            pass
        filename_pattern = os.path.basename(pattern)
        print(filename_pattern)
        directory_pattern = os.path.dirname(pattern)
        print(directory_pattern)

#######################################################################
#  Default Filewalker
#######################################################################


#  run_range
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


#  filenum
def is_filenum(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def get_filenum(string):
    try:
        return int(string)
    except ValueError:
        return None


#  n_files
def is_n_files(string):
    return fnmatch.fnmatch(string, '*Files')


def get_n_files(string):
    try:
        value = int(string.replace('Files', ''))
        return value
    except ValueError:
        return None


#  level_string
def is_level_string(string):
    matches = [fnmatch.fnmatch(string, 'level?'),
               fnmatch.fnmatch(string, 'level?_hdf5')]
    return any(matches)


def get_level_string(string):
    string = string.replace('level', '')
    string = string.replace('_hdf5', '')
    try:
        value = int(string)
        return value
    except ValueError:
        return None


default_filewalker = DukeFilewalker()
default_filewalker.register_kw('run_range',
                               is_valid_func=is_run_range,
                               get_value_func=get_run_range,
                               generation_func=generate_run_range,
                               for_='both')
default_filewalker.register_kw('filenum',
                               is_valid_func=is_filenum,
                               get_value_func=get_filenum,
                               for_='both')

default_filewalker.register_kw('n_files',
                               is_valid_func=is_n_files,
                               get_value_func=get_n_files,
                               for_='both')

default_filewalker.register_kw('level_string',
                               is_valid_func=is_level_string,
                               get_value_func=get_level_string,
                               for_='both')

default_filewalker.register_kw('year')
default_filewalker.register_kw('dataset_id')
default_filewalker.register_kw('level_folder', for_='dir')
default_filewalker.register_kw('type_ending', for_='file')
default_filewalker.register_kw('level')
default_filewalker.register_kw('sim_dir', for_='dir')
default_filewalker.register_kw('data_dir', for_='dir')
