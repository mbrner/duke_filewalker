class Keyword:
    def __init__(self, name, is_valid=None, get_value=None, generate=None):
        self.name = name.lower()
        if is_valid is None:
            self.is_valid = lambda x: True
        elif callable(is_valid):
            self.is_valid = is_valid
        else:
            raise ValueError('\'is_valid\' can be None or a functions, '
                             'that get a string and return True/False '
                             'depending on the correctnes of the string.')
        if get_value is None:
            self.get_value = lambda x: x
        elif callable(get_value):
            self.get_value = get_value
        else:
            raise ValueError('\'get_value\' can be None or a function, '
                             'returning the value extracted from a '
                             'string!')

        if generate is None:
            self.generate = lambda x: str(x)
        elif callable(generate):
            self.generate = generate
        else:
            raise ValueError('\'generate\' can be None or a function, '
                             'generating a string form the input of the '
                             'output of "get_vale"!')

    def __str__(self):
        return self.name

    def __repr__(self):
        info_str = '{}'.format(self.name)
        if self.is_valid is None:
            info_str += ' (not validity check)'
        if self.get_value is None:
            info_str += ' (not func to extract a value)'
        return info_str

    def __eq__(self, string):
        return self.is_valid(string)

    def __ne__(self, string):
        return not self.is_valid(string)

    def __call__(self, *args, **kwargs):
        return self.generate(*args, **kwargs)
