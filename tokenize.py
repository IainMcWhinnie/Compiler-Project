import definitions

def isidentifier(token):
    """ Decides whether a string is a valid identifier (for variable etc)"""
    return token.isalpha() # <==== NEEDS CHANGED, will do for now
        
def iswhitespace(char):
    """ Decides whether the character passed is whitespace """
    if char in definitions.WHITESPACE:
        return True
    else:
        return False

def istoken(token):
    """ Decides whether a string is a valid token """
    if token in definitions.KEYWORDS:
        return True
    elif token in definitions.SYMBOLS:
        return True
    elif token in definitions.UNARY_OPS:
        return True
    elif token.isdecimal():
        return True
    elif isidentifier(token):
        return True
    else:
        return False

def gettokens(filename):
    """ Returns a list of tokens """

    # Read from a file containing the code to parse
    with open(filename) as f:
        data = f.read()

    tokens = []

    cur_tok = data[0] # Start with just the first character

    for next_char in data[1:]+' ': # Loops through every character ( extra whitespace added to catch last token )
        if istoken(cur_tok):                    # If the current token is valid
            if not istoken(cur_tok+next_char):  # Would the next character make token with this one?
                                                # If not then
                tokens.append(cur_tok)          # We've found a token of just this character

                # Is the next char whitespace or the start of a new token
                if iswhitespace(next_char):
                    cur_tok = '' # Its just whitespace, forget about it
                else:
                    cur_tok = next_char # the next char starts a token

            else:
                # The current token is not a token on its own and we should concatenate the next character
                cur_tok += next_char

        else:
            # Current string is not a token
            if iswhitespace(cur_tok):
                # Could be whitespace
                cur_tok = ''
            else:
                # Could be part of a new token
                cur_tok += next_char

    return tokens


class TokenGenerator:
    # Creates a 'generator' that can be called on with next() but also has .peak() functionality to look ahead

    def __init__(self, filename):
        # get tokens from file
        self.tokens = gettokens(filename)
        self.i = 0

    # overload the next() method
    def __next__(self):
        # check that tokens[i] exists
        if self.i < len(self.tokens):
            value = self.tokens[self.i]
            self.i += 1
            return value
        else:
            # else raise similar error to a generator
            raise StopIteration

    # look one value ahead but don't increase i
    def peak(self):
        if self.i < len(self.tokens):
            return self.tokens[self.i]
        else:
            return None