import sys
import lexer

# for grammar
# S -> <identifier> = Expr
# Expr -> Mul Sum'
# Sum' -> eps|+ Mul Sum'|- Mul Sum'
# Mul -> Term Mul'
# Mul' -> eps|* Term Mul'|/ Term Mul'
# Term -> (Expr)|<identifier>|<number>|-Term

class InterpeterError(Exception):
    def __init__(self, pos, line, message):
        super().__init__(f'Interpeter error at position {pos} in line \n\t{line}\n\t{" "*(pos) + "^"}\n{message}\n')

class Interpeter():
    def __init__(self):
        self.names = {}
        self.lexer = lexer.Lexer()
    
    def evaluate_Term(self, tokens, pos):
        # Term -> (Expr)|<identifier>|<number>|-Term
        if pos >= len(tokens):
            raise InterpeterError(len(self.input), self.input, 'There should be IDENTIFIER or NUMBER or LEFT PARENTHESIS or MINUS')
        if tokens[pos].type == 'IDENTIFIER':
            if tokens[pos].val not in self.names:
                raise InterpeterError(tokens[pos].pos, self.input, f'"{tokens[pos].val}" is not defined')
            return self.names[tokens[pos].val], pos + 1

        elif tokens[pos].type == 'NUMBER':
            return int(tokens[pos].val), pos + 1

        elif tokens[pos].type == 'LP':
            result, pos = self.evaluate_expression(tokens, pos + 1)
            if pos >= len(tokens):
                raise InterpeterError(len(self.input), self.input, 'There should be RIGHT PARENTHESIS')
            if tokens[pos].type != 'RP':
                raise InterpeterError(tokens[pos].pos, self.input, 'There should be RIGHT PARENTHESIS')
            return result, pos + 1
        
        elif tokens[pos].type == 'MINUS':
            term, pos = self.evaluate_Term(tokens, pos + 1)
            return -term, pos

        else:
            raise InterpeterError(tokens[pos].pos, self.input, 'There should be NUMBER or IDENTIFIER or LEFT PARENTHESIS or MINUS')

    def evaluate_Mul_(self, acc, tokens, pos):
        # Mul' -> eps|* Term Mul'|/ Term Mul'
        if pos == len(tokens):
            return acc, pos
        elif tokens[pos].type == 'MULTIPLY':
            term, pos = self.evaluate_Term(tokens, pos + 1)
            acc *= term
            return self.evaluate_Mul_(acc, tokens, pos) 
        elif tokens[pos].type == 'DIVIDE':
            term, pos = self.evaluate_Term(tokens, pos + 1)
            acc /= term
            return self.evaluate_Mul_(acc, tokens, pos)  
        else:
            return acc, pos

    def evaluate_Mul(self, tokens, pos):
        # Mul -> Term Mul'
        term, pos = self.evaluate_Term(tokens, pos)
        return self.evaluate_Mul_(term, tokens, pos)
    
    def evaluate_Sum_(self, acc, tokens, pos):
        # Sum' -> eps|+ Mul Sum'|- Mul Sum'
        if pos == len(tokens):
            return acc, pos
        elif tokens[pos].type == 'PLUS':
            result, pos = self.evaluate_Mul(tokens, pos + 1)
            acc += result
            return self.evaluate_Sum_(acc, tokens, pos) 
        elif tokens[pos].type == 'MINUS':
            result, pos = self.evaluate_Mul(tokens, pos + 1)
            acc -= result
            return self.evaluate_Sum_(acc, tokens, pos)  
        else:
            return acc, pos
    
    def evaluate_expression(self, tokens, pos):
        # Expr -> Mul Sum'
        acc, pos = self.evaluate_Mul(tokens, pos)
        result, pos = self.evaluate_Sum_(acc, tokens, pos)
        return result, pos

    
    def evaluate_input(self, input):
        self.input = input
        self.lexer.input(input)
        tokens = self.lexer.tokens()
        if len(tokens) < 3:
            raise InterpeterError(0, self.input, 'There are should be at least three tokens in the input line')
        token0 = tokens[0]
        if token0.type != 'IDENTIFIER':
            raise InterpeterError(0, self.input, 'Expression should start with IDENTIFIER')
        token1 = tokens[1]
        if token1.type != 'EQUALS':
            raise InterpeterError(token1.pos, self.input, 'Second token in expression should be "="')
        result, pos = self.evaluate_expression(tokens[2:], 0)
        if pos < len(tokens) - 2:
            raise InterpeterError(tokens[pos-2].pos, self.input,'Expression is not valid')
        self.names[token0.val] = result
        return self.make_answer(token0.val)

    def make_answer(self, identifier_name):
        name = identifier_name
        value = self.names[name]
        return f'{name} = {value}'

def main():
    interpeter = Interpeter()
    lines = [
        'a = ((2))',
        'c = -a - 2',
        'd = c - a',
    ]
    # for line in sys.stdin:
    for line in lines:
        result = interpeter.evaluate_input(line)
        print(result)

if __name__ == '__main__':
    main()
