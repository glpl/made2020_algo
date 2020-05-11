import pytest 

from lexer import Lexer, LexerError, Token 
from interpeter import Interpeter, InterpeterError

def test_lexer_unknown_symbol():
    lexer = Lexer()
    lexer.input('a = # 1')
    with pytest.raises(LexerError, match='position 4 '):
        lexer.tokens()


def test_lexer():
    lexer = Lexer()
    lines = [
        ('a = 1', [
            Token('IDENTIFIER', 'a', 0), 
            Token('EQUALS', '=', 2), 
            Token('NUMBER', '1', 4)
        ]),
        ('a = (1 + 3) - b', [
            Token('IDENTIFIER', 'a', 0), 
            Token('EQUALS', '=', 2), 
            Token('LP', '(', 4),
            Token('NUMBER', '1', 5),
            Token('PLUS', '+', 7),
            Token('NUMBER', '3', 9),
            Token('RP', ')', 10),
            Token('MINUS', '-', 12),
            Token('IDENTIFIER', 'b', 14),
        ]),
        (' ', [])
    ]
    for line, right_tokens in lines:
        lexer.input(line)
        tokens = lexer.tokens()
        assert len(tokens) == len(right_tokens)
        for i in range(len(tokens)):
            assert tokens[i].type == right_tokens[i].type
            assert tokens[i].val == right_tokens[i].val
            assert tokens[i].pos == right_tokens[i].pos


def test_interpreter_wrong_start():
    interpeter = Interpeter()
    with pytest.raises(InterpeterError, match='Expression should start with IDENTIFIER'):
        interpeter.evaluate_input('= 1 + 2')
    with pytest.raises(InterpeterError, match='There are should be at least three tokens in the input line'):
        interpeter.evaluate_input('a =')
    with pytest.raises(InterpeterError, match='Expression should start with IDENTIFIER'):
        interpeter.evaluate_input('1 + 2')
    with pytest.raises(InterpeterError, match='Second token in expression should be "="'):
        interpeter.evaluate_input('a + b')


def test_interpreter_syntax_error():
    interpeter = Interpeter()
    with pytest.raises(InterpeterError, match='Expression is not valid'):
        interpeter.evaluate_input('a = 1 - 2)',)
    with pytest.raises(InterpeterError, match='There should be NUMBER or IDENTIFIER or LEFT PARENTHESIS or MINUS'):
        interpeter.evaluate_input('a = 1 +/ 2')
    with pytest.raises(InterpeterError, match='There should be RIGHT PARENTHESIS'):
        interpeter.evaluate_input('a = ((1 + 2) + 3')
    with pytest.raises(InterpeterError, match='There should be IDENTIFIER or NUMBER or LEFT PARENTHESIS or MINUS'):
        interpeter.evaluate_input('a = 1 *')


def test_uknown_variable():
    interpeter = Interpeter()
    with pytest.raises(InterpeterError, match='"b" is not defined'):
        interpeter.evaluate_input('a = 1 + b')


def test_interpreter():
    interpeter = Interpeter()
    lines = [
        ('a = 2', 'a = 2'),
        ('b = 3', 'b = 3'),
        ('c = 2 * 5', 'c = 10'),
        ('d = c - a', 'd = 8'),
        ('x = a / c', 'x = 0.2'),
        ('x = -1 + b', 'x = 2')
    ]
    for input, output in lines:
        assert output == interpeter.evaluate_input(input)
