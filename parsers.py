
# Top down definition of Abstract Syntax Tree

# <program> ::= <function>
# <function> ::= "int" <id> "(" ")" "{" <statement> "}"
# <statement> ::= "return" <exp> ";"
# <exp> ::= <unary_op> <exp> | <int>
# <unary_op> ::= "!" | "~" | "-"

# Lol check out C's BNF
# https://cs.wmich.edu/~gupta/teaching/cs4850/sumII06/The%20syntax%20of%20C%20in%20Backus-Naur%20form.htm

#----------------------------------------------------------------------------------------#

from ast import Program, Function, Statement, UnaryOpExpression, Integer, UnaryOp
import definitions

#----------------------------------------------------------------------------------------#

def parse_program(genrt):
    # The BNR defines a program as just a function
    # <program> ::= [<function>]*
    functions = []
    while not genrt.peak() is None:
        functions.append(parse_function(genrt))

    # Create a new program and return it
    new_program = Program(functions)
    return new_program

#----------------------------------------------------------------------------------------#


def parse_function(genrt):
    # BNR: <function> ::= "int" <id> "(" ")" "{" <statement> "}"

    # assert that the return type is 'int'
    return_type = next(genrt)
    assert return_type == 'int'

    # get the function id
    id = next(genrt)

    # assert the '(', ')' and '{' tokens
    assert next(genrt) == '('
    assert next(genrt) == ')'
    assert next(genrt) == '{'

    # get the statement parse
    statement = parse_statement(genrt)

    # assert the final '}'
    assert next(genrt) == '}'

    # create the new function and return it
    new_function = Function(id, statement)
    return new_function
    


#----------------------------------------------------------------------------------------#



def parse_statement(genrt):
    # BNR <statement> ::= "return" <exp> ";"

    # assert the return part
    assert next(genrt) == 'return'

    # get the expression
    expression = parse_expression(genrt)

    # assert the semicolon
    assert next(genrt) == ';'

    # create and return the statement
    new_statement = Statement(expression)
    return new_statement

#----------------------------------------------------------------------------------------#



def parse_expression(genrt):
    # <exp> ::= <unary_op> <exp> | <int>
    
    # first consider the next token
    next_token = genrt.peak()

    # is the next token a unary op
    if next_token in definitions.UNARY_OPS:
        # Then the form must be
        # <exp> ::= <unary_op> <exp>
        unary_op = parse_unaryop(genrt)
        expression = parse_expression(genrt)
        new_expression = UnaryOpExpression(unary_op, expression)
        #new_expression = Expression(new_expression_child)
    else:
        # then the form must be 
        # <exp> ::= <int>
        value = next(genrt)

        # create and return the expression
        new_expression = Integer(value=value)

    return new_expression




#----------------------------------------------------------------------------------------#


def parse_unaryop(genrt):
    # <unary_op> ::= "!" | "~" | "-"

    # just get the operator as a token
    operator = next(genrt)
    
    # create and return the new unaryop
    new_unaryop = UnaryOp(operator)
    return new_unaryop



#----------------------------------------------------------------------------------------#


if __name__=='__main__':
    import tokenize
    token_generator = tokenize.TokenGenerator('test.c')
    x = parse_program(token_generator)
    print(x.generate_code())