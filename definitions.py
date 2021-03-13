



UNARY_OPS = ['!', '~', '-']
KEYWORDS = ['int', 'return']
SYMBOLS = ['(', ')', '{', '}', ';']

WHITESPACE = ['\t','\n',' ']


# <program> ::= <function>
# <function> ::= "int" <id> "(" ")" "{" <statement> "}"
# <statement> ::= "return" <exp> ";"
# <exp> ::= <unary_op> <exp> | <int>
# <unary_op> ::= "!" | "~" | "-"

#  [+-]?(   (    [0-9]+(.[0-9]∗)?  |   .[0-9]+   )     ([eE][+-]?[0-9]+)?    )
