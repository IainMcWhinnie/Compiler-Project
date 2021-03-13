######################### LEXER.py ###############################



# Given a regex description of the language syntax and parsing priority
# tokenize the input file and return a iterator for parsing



#-----------------------------------------------------------------------------------------------------------#
# For each piece of programming syntax describe:
# --> A regex expression
# --> Key to pass on the parser (ID)
# --> Any other additional info ( ie an action )

#List of dictionaries

language = [{'regex':'int|void',    'key':'TYPE'},
            {'regex':'return',      'key':'RETURN'},
            {'regex':';',           'key':'END STATEMENT'},
            {'regex':'[(){}\\[\\]]',      'key':'BRACKETS'},
            {'regex':'[0-9]+',      'key':'INTEGER'},
            {'regex':'[a-zA-Z][a-zA-Z0-9]*', 'key':'IDENTIFIER'}
]

lowercase_alphabet = list('abcdefghijklmnopqrstuvwxyz')
uppercase_alphabet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
digits = list('0123456789')


#-----------------------------------------------------------------------------------------------------------#


# How to create a NFA 

# Todo:
#   Create NFA data structure
#   Parse Regex Expression
#   Modify the NFA using the language definition regex


#-----------------------------------------------------------------------------------------------------------#

#   Create NFA data structure

# NFA is a directed graph with numbered vertices

# For each regex operator define how it is turned into a NFA graph
# define a function for each regex operator that takes parameters:
# regex_op(NFA_graph, input_node, regex_parameters)
# and modifies the NFA appropriately returning the new node index
# Note: the function can recursively handle the regex nesting


# The graph data structure as a dictionery indexed by tuples where
# (s,d) -> referes to connection from s to d
# The values stored will either be EPSILON or a character from the language
# in a list naming all the connections

# Example NFA

# REGEX: (a|b)c
# NFA:
#                 e        e       a
#     ------> 1 -----> 2 ----> 3 -----|
#                      |              |
#                      |-----> 4 ---> 5 ----> 6
#                         e        b      c
#
# REPRESENTATION:
# graph = {(1,2):[e],
#         (2,3):[e],
#         (2,4):[e],
#         (3,5):['a'],
#         (4,5):['b'],
#         (5,6):['c']
# }


# The graph data structure with be held within a Graph object which will
# have methods for adding edges and finding neighbours

class Graph():

    def __init__(self, size=0):
        # Define the graph structure as above
        self.graph = {}

        # The node names should be numbered between 0 and the graph size
        # Defaults to 0
        self.size = size

    def add_node(self):
        # Returns a number to identify a new graph node

        new_node = self.size # The new number is the size of the graph
                             # ie when the graph is empty the first node
                             # created will be named 0 then 1,2,3...
        self.size = self.size + 1 # Increase the size by 1

        return new_node

    def add_edge(self, source, target, value):
        # The add edge method for our graph structure
        # (s,d) -> referes to connection from s to d

        #Check the source and target values are in range
        assert 0 <= source and source < self.size, 'Source value out of graph range'
        assert 0 <= target and target < self.size, 'Target value out of graph range'

        # Create the edge
        self.graph[(source, target)] = self.graph.get((source,target),[])+[value]

    def get_neighbours(self, node, value):
        # Return all the edges a node has with a given edge value
        neighbours = [] # Init an array to collect neighbours

        for i in range(self.size): # For ever other node identifier
            # Get the edge from the graph
            edge = self.graph.get((node, i), [])
            if value in edge: # If the edge exists and has the correct value
                neighbours.append(i) # Add the node id to array
        
        return neighbours




# Create the placeholder for Epsilon values
EPSILON = 'EPSILON'

# Create the NFA graph
NFA = Graph()


#-----------------------------------------------------------------------------------------------------------#


#   Parse Regex Expression

# Regex can be parsed to create a NFA graph in four basic ways
#
# ab: Creates a chain link in the graph
# a|b: Creates two paths which have each option
# a*: Creates a loop back to initial node
# a+: Creates a loop with extra link and a one way connection

# Regex operators have a precedence
# 0: Brackets
# 1: * Operator 
# 2: + Operator 
# 3: Concatenation  
# 4: | Operator

# However our Regex expressions use more complex operators to simplify
# what would be complicated regex expressions
# More compilcated Regex:
# Square Brackets [abcd] ::= (a|b|c|d)
# Square Brackets with range [0-9] ::= (0|1|2|3|4|5|6|7|8|9)      (Only comes as a-z, A-Z, 0-9)

# Additionally if the regex operations can be escaped by the backslash to be used as normal strings

# Define a function that will reduce the regex to the four basic operations

def reduce_regex(exp):
    # We only should find the most deeply nested square brackets first
    # Search for the first close bracket
    # We will recursively eliminate the most deeply nested brackets and from left to right

    # We need to be careful to avoid square brackets that have been escaped in the regex strings

    # Get index of the first closing bracket ']'
    end_brck_inx = exp.find(']')
    while end_brck_inx != -1: # While a bracket is still findable
        if exp[end_brck_inx-1] == '\\': # If the bracket character is escaped
            end_brck_inx = exp.find(']', end_brck_inx) # Try again
        else:
            # The bracket exist and is not escaped so is the correct one so stop iteration
            break

    # First the base case where the regex has no brackets
    if end_brck_inx == -1:
        return exp

    # Divide the expression into 2 parts around the closing bracket
    tail_end = exp[(end_brck_inx+1):]
    front_end = exp[:end_brck_inx]
    
    # Now we should search the front end for the last opening bracket to get a pair
    strt_brck_inx = front_end.rfind('[')
    while strt_brck_inx != -1: # While a bracket is still findable
        if front_end[strt_brck_inx-1] == '\\': # If the bracket character is escaped
            strt_brck_inx = front_end.find('[', 0, strt_brck_inx) # Try again with end set to the previous index
        else:
            # The bracket exist and is not escaped so is the correct one so stop iteration
            break

    # Now we can get three pieces
    inside_exp = front_end[strt_brck_inx+1:]
    front_end = front_end[:strt_brck_inx]
    # and tail_end

    #print('a',front_end,'n', inside_exp, 'f',tail_end)

    # Now we should expand the notation in inside expression
    # We will create a list of all the possible options and then we will concatenate at the end
    options = []

    # First we should check for our range notation
    if 'a-z' in inside_exp:
        # get rid of our shorthand notation and add the lowercase alphabet to our list
        inside_exp = inside_exp.replace('a-z','')
        options.extend(lowercase_alphabet)

    if 'A-Z' in inside_exp:
        # get rid of shorthand and add uppercase alphabet
        inside_exp = inside_exp.replace('A-Z','')
        options.extend(uppercase_alphabet)

    if '0-9' in inside_exp:
        # get rid of shorthand and add digits
        inside_exp = inside_exp.replace('0-9','')
        options.extend(digits)

    # now we can add the other characters in our brackets and add them to options
    # because of escaped characters we dont know how wide each element is and
    # we will iterate with a while loop
    # Our implementation assumes no repeats but a repeat will not raise error
    i = 0
    while i<len(inside_exp):
        if inside_exp[i] == '\\':
            # get the character meant to be escaped
            escaped_char = inside_exp[i+1]
            # add it along side it backslash as one item
            options.append('\\'+escaped_char)
            # increase the counter by 2
            i += 2
        else:
            # not an escaped character simply append and increment the counter
            options.append(inside_exp[i])
            i += 1

    # Our new inside_exp is all the options seperated by bars and surrounded by brackets
    new_inside_exp = '('+'|'.join(options)+')'

    # Reassembling our expression we get
    exp = front_end+new_inside_exp+tail_end

    #print('Yes its now: ',exp)
    # Now we recursively call this function on it until all brackets are gone
    return reduce_regex(exp)


# Now we need to parse our reduced regex into a NFA graph

# Define a function that takes parameters:
# Exp - a regex expression
# Graph - a NFA graph
# Input node name
# Output node name

def regex_to_NFA(exp, graph, input_node, end_node):
    # First we need to clean our regex to get rid of complicated syntax
    exp = reduce_regex(exp)
    
    # Now we should ommit the brackets in our answer for recursive parsing
    # We should iterate over the exp and split the string at the highest level
    # of bracket
    # 
    # eg. convert   a|b|c(a|b*)(aa(d|dd))+
    # to  a|b|c()()+
    # and collect the nested bracket contents in an array
    brckt_conts = []

    i = exp.find('(') # find the first starting bracket
    while i > 0 and exp[i-1] == '\\': # if the character is escaped
        i = exp.find('(', i+1) # try again

    nesting_level = 0 # how many brackets have we already seen

    while i<len(exp) and i != -1:
        # now create an empty string for the bracket contents
        brckt_contents = ''

        starting_i = i # save the starting position of the brackets for use later

        # now iterate over the expression until we find a closing brackt that matches the level
        i += 1 # start at the next character

        escape = False # set escapement boolean to false

        while i < len(exp): 
            # while we havent found the matching closing bracket
            if exp[i] == ')' and nesting_level == 0 and not escape:
                break

            if exp[i] == '(' and not escape: # If there is a new opening bracket that isnt escaped
                nesting_level += 1 # then increase the nesting_level

            elif exp[i] == ')' and not escape: # If there is a closing bracket that isnt escaped
                nesting_level -= 1 # then decrease the nesting_level

            # Handle escapement
            if exp[i] == '\\' and not escape: # If there is an unescaped escape char
                escape = True # Set escape to be true
            else:
                escape = False # Either turn escape off or do nothing

            # We havent found the closing bracket so 
            # add the contents to the contents string
            brckt_contents += exp[i]
            
            
            i += 1 # increment i

            #print('Checking ', exp[i], nesting_level)

        brckt_conts.append(brckt_contents) # add the contents of the bracket to the list

        # delete the contents of the bracket from the exp string and replace them with hashes eg (#####)
        # this operation preserves the length of the string which is important for the function to work
        exp = exp[:starting_i+1] + '#'*len(brckt_contents) + exp[i:]

        i = exp.find('(',i) # now we find the next opening bracket to repeat the process
        while i > 0 and exp[i-1] == '\\': # if the character is escaped
            i = exp.find('(', i+1) # try again
    
    exp = exp.replace('#','') # get rid of the hash symbols
    ## FIX FOR ESCAPED CHARACTERS

    print('A list of the bracket contents:',brckt_conts,'\nExp:',exp)

    # Now we start by dividing the expression into the lowest precedence operator |
    # We treat the empty bracket pairs () as single elements and retrieve their contents
    # from the list.

    # From the input node we create as many branches as there is options

    # FIX FOR ESCAPED CHARACTERS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    options = exp.split('|')

    for branch in options:
        print('Creating a branch for ',branch)
        # First we create a node for each option
        node = graph.add_node()
         
        # Then we add an edge to the node from the input with the value EPSILON
        graph.add_edge(input_node, node, EPSILON)

        # Now we can parse from the highest precence in each  (*, +, concat)

        # first we should implement the recursive base case where the regex is 1 character
        # and the case where the regex is just brackets

        if len(branch) == 1:
            # The regex is just one character
            graph.add_edge(node, end_node, branch)
        elif branch == '()':
            # The regex is our empty bracket notation so we pop the contents from brckt_conts list
            # first in first out so take from the start
            contents = brckt_conts.pop(0)
            regex_to_NFA(contents, graph, node, end_node)
        elif len(branch) == 2 and branch[0] == '\\':
            # The regex is a single escaped character
            graph.add_edge(node, end_node, branch)
        else:
            # The regex statement either has more than one character or uses +,* operators
            # First create a list of elements in concatentation bound by +,*
            parts = []
            i = 0 # We iterate through with a while since we do not know how many elements
            current_elm = ''
            while i < len(branch):
                if i != 0 and branch[i] == '+' or branch[i] == '*' and branch[i-1] != '\\':
                    # Check for unescaped operators
                    current_elm += branch[i]
                elif branch[i] == '\\':
                    # The current char together with the next one form an escaped character
                    # Add the previous item
                    if i != 0:
                        parts.append(current_elm)
                    # Add the escaped char to the cur item buffer
                    assert i+1 < len(branch), 'Esacpement used without character'
                    current_elm = branch[i]+branch[i+1]
                    i += 1 # we will end up incrementing i by 2 in this loop
                else:
                    # The current index is the start of a new item
                    # Add the previous item
                    parts.append(current_elm)
                    # Restart the current_elm buffer
                    current_elm = branch[i]

                i += 1

            parts.append(current_elm) # Append the last item (not done by while loop)

            print(parts)
                    

    

    

if __name__=='__main__':
    input_node = NFA.add_node()
    output_node = NFA.add_node()
    regexParse = input('Regex to parse: ')
    regex_to_NFA(regexParse, NFA, input_node, output_node)
    print('Input Node: ',input_node)
    print('Ouput Node: ',output_node)
    print(NFA.graph)