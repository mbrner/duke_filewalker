from __future__ import division, absolute_import
from __future__ import with_statement, print_function
import re
import difflib
import fnmatch


def get_keywords(pattern):
    return re.findall(r'\<(.*?)\>', pattern)


def generate_fnmatch_pattern(pattern):
    keywords = get_keywords(pattern)
    for kw in keywords:
        pattern = pattern.replace('<{}>'.format(kw), '*')
    return pattern, keywords


def extract(string, pattern):
    pattern, keywords = generate_fnmatch_pattern(pattern)
    splitted_pattern = pattern.split('*')
    extraction = {}
    tmp = str(string)
    for i, split_i in enumerate(splitted_pattern):
        if split_i == '':
            continue
        replacement, got_it, tmp = tmp.partition(split_i)
        if got_it == '':
            break
        if replacement != '':
            if i == 0 and not pattern.startswith('*'):
                continue
            extraction[keywords[len(extraction)]] = replacement
    if tmp != '':
        extraction[keywords[len(extraction)]] = tmp
    return extraction


def extract_2(string, pattern, keywords):
    extraction = {}
    pointer = 0
    match = ''
    in_ = False
    for c, _, s in difflib.ndiff(pattern, string):
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
                    'Unexpected str found: {} {}'.format(pattern,
                                                         string))
            extraction[keywords[pointer]] = match
            match = ''
            pointer += 1
    if in_:
        if len(match) == 0:
            pass
        else:
            extraction[keywords[pointer]] = match
    return extraction


class Pattern(str):
    def __init__(self, pattern):
        self.pattern = pattern
        self.keywords = get_keywords(self.pattern)
        self.fnmatch_pattern = pattern
        for kw in self.keywords:
            self.fnmatch_pattern = self.fnmatch_pattern.replace(
                '<{}>'.format(kw), '*')

    def __add__(self, other):
        if isinstance(other, Extraction):
            new_pattern = self.pattern
            for kw in self.keywords:
                if kw in other.keys():
                    replacement = other[kw]
                    new_pattern = new_pattern.replace(
                        '<{}>'.format(kw), replacement)
            return Pattern(new_pattern)
        else:
            return super(Pattern, self).__add__(other)

    def __radd__(self, other):
        return self + other

    def match(self, string):
        return fnmatch.fnmatch(string, self.fnmatch_pattern)

    def extract(self, string, match=True):
        if match:
            if not self.match(string):
                raise ValueError('{} is not matching {}'.format(string, self))
        file_dict = extract(string, self.pattern)
        return Extraction(file_dict)


class Extraction(dict):
    def __add__(self, other):
        if isinstance(other, Pattern):
            return other + self
        elif isinstance(other, dict):
            for kw in other.keys():
                if kw not in self.keys():
                    try:
                        new_entry = str(other[kw])
                    except ValueError:
                        pass
                    else:
                        self[kw] = new_entry
            return self
        elif isinstance(other, str):
            other = Pattern(other)
            return other + self
        else:
            TypeError('Only "Pattern" and "Extraction" objects can be added')

    def __radd__(self, other):
        return self + other
