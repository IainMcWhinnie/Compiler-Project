
# Top down definition of Abstract Syntax Tree

# <program> ::= <function>
# <function> ::= "int" <id> "(" ")" "{" <statement> "}"
# <statement> ::= "return" <exp> ";"
# <exp> ::= <unary_op> <exp> | <int>
# <unary_op> ::= "!" | "~" | "-"

# Lol check out C's BNF
# https://cs.wmich.edu/~gupta/teaching/cs4850/sumII06/The%20syntax%20of%20C%20in%20Backus-Naur%20form.htm


class Program:
    def __init__(self, functions):
        self.functions = functions

    def generate_code(self):
        print(self)
        functions_code = '\n'.join([f.generate_code() for f in self.functions])
        return functions_code


class Function:
    def __init__(self, id, statement):
        self.id = id
        self.statement = statement

    def generate_code(self):
        name = '_'+self.id + ':\n'
        body = self.statement.generate_code()
        return name+body


class Statement:
    def __init__(self, expression):
        self.expression = expression

    def generate_code(self):
        code = self.expression.generate_code('eax') + '\n\tret'
        return code


# <exp> ::= <unary_op_exp> | <int>

class UnaryOpExpression():
    # <unary_op_exp> ::= <unary_op> <exp>
    def __init__(self, unary_op, expression):
        self.unary_op = unary_op
        self.expression = expression

    def generate_code(self, register):
        code = self.expression.generate_code(register)+'\tOPY '+register
        return code

    def __str__(self):
        pass

class Integer():
    # <int> ::= value
    def __init__(self, value):
        self.value = value

    def generate_code(self, register):
        code = '\tmov '+register+', '+self.value+'\n'
        return code

    def __str__(self):
        return self.value





class UnaryOp:
    def __init__(self, operation):
        self.operation = operation

    def __str__(self):
        return 'UNARYOP('+self.operation+')'
