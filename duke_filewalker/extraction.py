from __future__ import division, absolute_import
from __future__ import with_statement, print_function
import re
import difflib
import fnmatch


def adjust_slash_at_end(string, pattern):
    if pattern.endswith('/') and not string.endswith('/'):
        return string + '/'
    elif string.endswith('/') and not pattern.endswith('/'):
        return string[:-1]
    else:
        return string


def get_keywords(pattern):
    string_list = re.findall(r'\<(.*?)\>', pattern)
    return [Keyword(string) for string in string_list]


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
    for i, keyword_i in enumerate(keywords):
        pass

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
        self.keywords = get_keywords(pattern)
        self.pattern = pattern
        for kw in self.keywords:
            self.pattern = self.pattern.replace(repr(kw), str(kw))
        self.fnmatch_pattern = self.pattern
        for kw in self.keywords:
            self.fnmatch_pattern = self.fnmatch_pattern.replace(
                '<{}>'.format(kw), '*')

    def __add__(self, other):
        if isinstance(other, dict) and not isinstance(other, Extraction):
            other = Extraction(other)
        if isinstance(other, Extraction):
            new_pattern = self
            for kw in self.keywords:
                if kw in other.keys():
                    replacement = other[kw]
                    try:
                        replacement = str(replacement)
                    except:
                        pass
                    else:
                        new_pattern = new_pattern.replace(
                            '<{}>'.format(repr(kw)), replacement)
            return Pattern(new_pattern)
        else:
            return super(Pattern, self).__add__(other)

    def __radd__(self, other):
        return self + other

    def __fnmatch__(self, string, pattern=None):
        if pattern is None:
            pattern = self.fnmatch_pattern
        matches = fnmatch.fnmatch(string, pattern)
        if not matches and string.endswith('/'):
            matches = fnmatch.fnmatch(string, pattern + '/')
        elif not matches and pattern.endswith('/'):
            matches = fnmatch.fnmatch(string + '/', pattern)
        return matches

    def match(self, string, extract=False, sub=False):
        if self.__fnmatch__(string):
            extraction = self.extract(string)
            checked_extraction = [kw.match(extraction[kw], sub=sub)
                                  for kw in self.keywords
                                  if kw in extraction.keys()]
            if extract:
                return all(checked_extraction), extraction
            else:
                return all(checked_extraction)
        else:
            if extract:
                return False, {}
            else:
                return False

    def match_subpath(self, string, extract=False):
        try:
            reduced_pattern, reduced_fnmatch = self.reduce_pattern(string)
        except ValueError:
            raise ValueError('A pattern starting with a keyword without '
                             'a depth limit can not bebe used for '
                             'match_subpath, because \'*\' '
                             'matches with everything!')
        if reduced_pattern is None:
            return False
        reduced_pattern = Pattern(reduced_pattern)
        if extract:
            matching, extraction = reduced_pattern.match(string,
                                                         extract=True,
                                                         sub=True)
            return matching, reduced_pattern, extraction
        else:
            return reduced_pattern.match(string, sub=True)

    def reduce_pattern(self, string):
        if self.fnmatch_pattern.startswith('*'):
            if self.keywords[0].depth is None:
                raise ValueError
        splitted_pattern = self.fnmatch_pattern.split('*')
        pattern_fragments = [splitted_pattern[0]]
        if len(splitted_pattern) > 1:
            for split_i in splitted_pattern[1:]:
                pattern_fragments.append('*')
                if '/' in split_i:
                    ss = []
                    while split_i != '':
                        pre, slash, split_i = split_i.partition('/')
                        ss.append(pre + slash)
                    pattern_fragments.extend(ss)
                else:
                    pattern_fragments.append(split_i)

        reduced_patterns = []
        for i in range(len(pattern_fragments) - 1):
            reduced_patterns.append(''.join(pattern_fragments[:i + 1]))
        matching = [self.__fnmatch__(string, pat) for pat in reduced_patterns]
        if not any(matching):
            return None, None
        else:
            idx = len(matching) - matching[::-1].index(True) - 1
            reduced_fnmatch = reduced_patterns[idx]
            reduced_pattern = ''
            kw_counter = 0
            for fragment_i in pattern_fragments[:idx + 1]:
                if fragment_i != '*':
                    addition = fragment_i
                else:
                    addition = '<{}>'.format(repr(self.keywords[kw_counter]))
                    kw_counter += 1
                reduced_pattern += addition
        reduced_pattern = adjust_slash_at_end(reduced_pattern, string)
        reduced_fnmatch = adjust_slash_at_end(reduced_fnmatch, string)
        return Pattern(reduced_pattern), reduced_fnmatch

    def extract(self, string, reduce=False):
        if reduce:
            pattern, _ = self.reduce_pattern(string)
        else:
            pattern = self.pattern
        string = adjust_slash_at_end(string, pattern)
        file_dict = extract(string, pattern)
        return Extraction(file_dict)

    def replace(self, *args):
        if len(args) == 2:
            return super(Pattern, self).replace(args[0], args[1])
        elif len(args) == 1:
            extraction = args[0]
            if isinstance(extraction, Extraction):
                new_pattern = self
                for kw in self.keywords:
                    if kw in extraction.keys():
                        replacement = extraction[kw]
                        try:
                            replacement = str(replacement)
                        except:
                            pass
                        else:
                            new_pattern = new_pattern.replace(
                                '<{}>'.format(repr(kw)), replacement)
                return Pattern(new_pattern)
            else:
                raise TypeError('\'extraction\' must be of type Extraction.')
        else:
            raise AttributeError('Either (str, str) or (Extraction)')


class Extraction(dict):
    def __add__(self, other):
        if isinstance(other, Pattern):
            return other + self
        elif isinstance(other, dict):
            for kw in other.keys():
                if kw not in self.keys():
                    try:
                        new_entry = other[kw]
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


class Keyword(str):
    def __new__(cls, name, *args, **kwargs):
        if '::' in name:
            name = name.split('::')[0]
        return super(Keyword, cls).__new__(cls, name)

    def __init__(self, string):
        self.input = string
        self.depth = None
        if '::' in string:
            splitted = string.split('::')
            for i, split_i in enumerate(splitted):
                if i == 0:
                    self.name = split_i
                else:
                    try:
                        self.depth = int(split_i)
                    except ValueError:
                        raise ValueError('Keywords have to be '
                                         '\'name::depth\'')
        else:
            self.name = string
            self.depth = 1

    def match(self, string, sub=False):
        if self.depth == 0:
            return True
        else:
            matches = True
            if string.startswith('/'):
                string = string[1:]
            if string.endswith('/'):
                string = string[:-1]
            if sub:
                has_required_depth = string.count('/') + 1 <= self.depth
            else:
                has_required_depth = string.count('/') + 1 == self.depth
            matches = matches and has_required_depth
            return matches

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.input

    def __hash__(self):
        return hash(self.name)

    def __cmp__(self, other):
        return str(self) == other

    def __eq__(self, other):
        return str(self) == other
