import re

rules = [
    ('\d+', 'NUMBER'),
    ('[a-zA-Z_]([a-zA-Z_0-9])*', 'IDENTIFIER'),
    ('\+', 'PLUS'),
    ('\-', 'MINUS'),
    ('\*', 'MULTIPLY'),
    ('\/', 'DIVIDE'),
    ('\(', 'LP'),
    ('\)', 'RP'),
    ('=', 'EQUALS'),
]

class Token(object):
    """ A simple Token structure.
        Contains the token type, value and position.
    """
    def __init__(self, type, val, pos):
        self.type = type
        self.val = val
        self.pos = pos


class LexerError(Exception):
    def __init__(self, pos, buf):
        super().__init__(f'Lexer error at position {pos} in line \n\t{buf}')


class Lexer(object):
    def __init__(self):
        idx = 1
        regex_parts = []
        self.group_type = {}

        for regex, type in rules:
            groupname = 'GROUP%s' % idx
            regex_parts.append('(?P<%s>%s)' % (groupname, regex))
            self.group_type[groupname] = type
            idx += 1

        self.regex = re.compile('|'.join(regex_parts))
        self.re_ws_skip = re.compile('\S')

    def input(self, buf):
        self.buf = buf
        self.pos = 0

    def token(self):
        if self.pos >= len(self.buf):
            return None
        else:
            m = self.re_ws_skip.search(self.buf, self.pos)

            if m:
                self.pos = m.start()
            else:
                return None

            m = self.regex.match(self.buf, self.pos)
            if m:
                groupname = m.lastgroup
                tok_type = self.group_type[groupname]
                tok = Token(tok_type, m.group(groupname), self.pos)
                self.pos = m.end()
                return tok

            # if we're here, no rule matched
            raise LexerError(self.pos, self.buf)

    def tokens(self):
        tokens = []
        while True:
            tok = self.token()
            if tok is None: 
                break
            tokens.append(tok)
        return tokens
       