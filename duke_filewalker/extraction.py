from __future__ import division, absolute_import
from __future__ import with_statement, print_function
import os
import re


def get_keywords(string):
    return re.findall(r'\<(.*?)\>', string)


class FilePath(str):
    def __init__(self, pattern):
        self.file_pattern = os.path.basename(pattern)
        self.file_keywords = get_keywords(self.file_pattern)
        self.dir_pattern = os.path.dirname(pattern)
        self.dir_keywords = get_keywords(self.dir_pattern)

    def __add__(self, other):
        if isinstance(other, Extraction):
            new_file_pattern = self.file_pattern
            for kw in self.file_keywords:
                if kw in other.file_dict.keys():
                    replacement = other.file_dict[kw]
                    new_file_pattern = new_file_pattern.replace(
                        '<{}>'.format(kw), replacement)
            new_dir_pattern = self.dir_pattern
            for kw in self.dir_keywords:
                if kw in other.dir_dict.keys():
                    replacement = other.dir_dict[kw]
                    new_dir_pattern = new_dir_pattern.replace(
                        '<{}>'.format(kw), replacement)
            new_pattern = os.path.join(new_dir_pattern, new_file_pattern)
            return FilePath(new_pattern)
        else:
            return super(FilePath, self).__add__(other)

class Extraction:
    def __init__(self, file_dict, dir_dict):
        self.file_dict = file_dict
        self.dir_dict = dir_dict

    def __add__(self, other):
        if isinstance(other, FilePath):
            return other + self
        elif isinstance(other, Extraction):
            for kw in other.file_dict:
                if kw not in self.file_dict.keys():
                    self.file_dict[kw] = other.file_dict[kw]
            for kw in other.dir_dict:
                if kw not in self.dir_dict.keys():
                    self.dir_dict[kw] = other.dir_dict[kw]
            return self
        else:
            TypeError('Only "FilePath" and "Extraction" objects can be added')

