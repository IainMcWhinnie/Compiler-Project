######################### LEXER.py ###############################



# Given a regex description of the language syntax and parsing priority
# tokenize the input file and return a iterator for parsing



#-----------------------------------------------------------------------------------------------------------#

# Import some tools for lexical parsing escaped characters
import esc_tools


# For each piece of programming syntax describe:
# --> A regex expression
# --> Key to pass on the parser (ID)
# --> Any other additional info ( ie an action )

#List of dictionaries

language = [{'regex':'int|void',               'key':'TYPE'},
            {'regex':'return',                 'key':'RETURN'},
            {'regex':';',                      'key':'END STATEMENT'},
            {'regex':'[\\(\\){}\\[\\]]',       'key':'BRACKETS'},
            {'regex':'[0-9]+',                 'key':'INTEGER'},
            {'regex':'[0-9]+.[0-9]+',          'key':'FLOAT'},
            {'regex':'[a-zA-Z][a-zA-Z0-9]*',   'key':'IDENTIFIER'}
]

##    0-9: $   a-z:%   A-Z: @

lowercase_alphabet = list('abcdefghijklmnopqrstuvwxyz')
uppercase_alphabet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
digits = list('0123456789')

# Compute the character set
character_set = set()
for expression in language:
    # Expand the short hand notation
    new_chars = expression['regex'].replace('0-9',''.join(digits)\
                                    ).replace('a-z',''.join(lowercase_alphabet)\
                                    ).replace('A-Z',''.join(uppercase_alphabet))
    # get rid of symbols that are inherintly regex defined
    for regex_symbol in '[]()+|*':
        new_chars = esc_tools.replace_with_esc(new_chars, regex_symbol, '')

    # add the new characters
    for char in new_chars:
        character_set.add(char)



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

 

#-----------------------------------------------------------------------------------------------------------#


#   Parse Regex Expression

# Regex can be parsed to create a NFA graph in four basic ways
#
# ab: Creates a chain link in the graph
# a|b: Creates two paths which have each option
# a*: Creates a loop back to initial node
# a+: Creates a loop with extra link and a one way connection (so must run at least once)

# Regex operators have a precedence
# 0: Brackets
# 1: *,+ Operator
# 2: Concatenation  
# 3: | Operator

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
    end_brck_inx = esc_tools.find_with_esc(exp, ']')

    # First the base case where the regex has no brackets
    if end_brck_inx == -1:
        return exp

    # Divide the expression into 2 parts around the closing bracket
    tail_end = exp[(end_brck_inx+1):]
    front_end = exp[:end_brck_inx]
    
    # Now we should search the front end for the last opening bracket to get a pair
    strt_brck_inx = esc_tools.rfind_with_esc(front_end, '[')

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

    #print('Cleaning complex syntax:')
    exp = reduce_regex(exp)
    #print('\tNew_exp:',exp)
    
    # Now we should ommit the brackets in our answer for recursive parsing
    # We should iterate over the exp and split the string at the highest level
    # of bracket
    # 
    # eg. convert   a|b|c(a|b*)(aa(d|dd))+
    # to  a|b|c()()+
    # and collect the nested bracket contents in an array
    brckt_conts = []

    i = esc_tools.find_with_esc(exp, '(') # find the first starting bracket

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

        brckt_conts.append(brckt_contents) # add the contents of the bracket to the list

        # delete the contents of the bracket from the exp string (Notice this changes the index i)
        exp = exp[:starting_i+1] + exp[i:]
        # the position i refered to in the old exp can now be indexed by starting_i+1

        i = esc_tools.find_with_esc(exp, '(',starting_i+1) # now we find the next opening bracket to repeat the process
        

    #print('Handling brackets')
    #print('\tNew exp:',exp,'\n\tBracket contents:',brckt_conts)

    # Now we start by dividing the expression into the lowest precedence operator |
    # We treat the empty bracket pairs () as single elements and retrieve their contents
    # from the list.

    # From the input node we create as many branches as there is options

    #print('Parsing Branches')

    # Create an array called options for each part split by | with escapement handling
    options = esc_tools.split_with_esc(exp, '|')
    #print('Options: ',options, exp)

    # now parse each branch individually
    for branch in options:
        #print('\tCreating a branch for ',branch)
        
        # We can parse from the highest precence in each  (*, +, concat)

        # first we should implement the recursive base case where the regex is 1 character
        # and the case where the regex is just brackets



        if len(branch) == 1:
            # The regex is just one character
            # First we create a node for the option
            node = graph.add_node()
            # Then we add an edge to the node from the input with the value EPSILON
            graph.add_edge(input_node, node, EPSILON)
            # Then connect the node to the output
            graph.add_edge(node, end_node, branch)




        elif branch == '()':
            # The regex is our empty bracket notation so we pop the contents from brckt_conts list
            # first in first out so take from the start
            contents = brckt_conts.pop(0)
            # recursively call the regex_to_NFA function
            regex_to_NFA(contents, graph, input_node, end_node)




        elif len(branch) == 2 and branch[0] == '\\':
            # The regex is a single escaped character
            # First we create a node for the option
            node = graph.add_node()
            # Then we add an edge to the node from the input with the value EPSILON
            graph.add_edge(input_node, node, EPSILON)
            # Then connect the node to the output
            graph.add_edge(node, end_node, branch)




        else:
            # The regex statement either has more than one character or uses +,* operators

            # Handle the case where the statement is a single (escaped?) character or brackets
            # that has + and * operations applied
            # Note that * overrules + and that nested + or * are the same as 1

            root = esc_tools.replace_with_esc(esc_tools.replace_with_esc(branch, '*',''),'+','')
            if len(root) == 1 or root == '()' or root[0]=='\\':
                extensions = esc_tools.replace_with_esc(branch, root, '')
                #print('\tNo concatenation!', extensions)
                # Two cases
                # Contains * or contains both
                # Contains +
                # Cant contain neither because the previous else clauses should handle that

                if '*' in extensions:
                    # Contains * or contains both
                    #print('\tMultiple')
                    # Implemented by a loop back to a node
                    # First of all create the node that the loop exits and returns to
                    loop_node = graph.add_node()
                    # Then add this node as an option for the branch
                    # Join to input and output with EPSILON
                    graph.add_edge(input_node, loop_node, EPSILON)
                    graph.add_edge(loop_node, end_node, EPSILON)

                    # Now recursively call this function on the root part passing both the input and output 
                    # as our loop node to create a loop

                    # first check whether we need to get contents from brackets
                    if root == '()':
                        root = brckt_conts.pop(0) # remove from start of bracket list
                    
                    regex_to_NFA(root, graph, loop_node, loop_node)

                else:
                    # Contains +
                    #print('\tAt least one')
                    # Implemented by two loop nodes that are joined with a link going backwards
                    # and the loop body defined by root
                    first_loop_node = graph.add_node()
                    scnd_loop_node = graph.add_node()
                    # connect the first node to the input
                    graph.add_edge(input_node, first_loop_node, EPSILON)
                    # add the backwards link
                    graph.add_edge(scnd_loop_node, first_loop_node, EPSILON)
                    # connect the second node to the output
                    graph.add_edge(scnd_loop_node, end_node, EPSILON)

                    # The loop body will again be a recursive call to this function passing the input as
                    # out first loop node and the output as our scnd loop node

                    # first check whether we need to get contents from brackets
                    if root == '()':
                        root = brckt_conts.pop(0) # remove from start of bracket list
                    
                    regex_to_NFA(root, graph, first_loop_node, scnd_loop_node)




            else:
                # In this case the branch is a string of concatenated statements with each
                # item possibly having *,+ operators on them
                # All we need to do is seperate each item and recursively call this function
                # on each

                # First create a list of elements in concatentation bound by +,*

                parts = []
                i = 0 # We iterate through with a while since we do not know how many elements
                current_elm = ''
                escaped = False
                ready = False

                # fails on \\+*

                for char in branch:

                    if ready and not char in '+*': # If the substring is a complete item and the
                                                   # current char is not a operator
                        # The current index is the start of a new item
                        # Add the previous item
                        parts.append(current_elm)
                        # Restart the current_elm buffer
                        current_elm = ''
                        ready = False

                    if escaped: # If the character is escaped add it to the buffer string
                        current_elm += char
                        escaped = False
                        ready = True

                    elif char == '\\': # If the character is an unescaped backslash then
                        current_elm += char # add the backslash to the buffer string
                        escaped = True # set escaped to True

                    else:
                        if char != '(':
                            ready = True
                        current_elm += char

                parts.append(current_elm) # Append the last item (not done by loop)

                #print(parts)

                # Now we have each part of the concatenation we just iterate through the graph
                # in a chain like structure
                # Each item gets a node with serves as its output and the next item's input
                # apart from the last node which uses the original output

                prev_output = input_node # first item gets the input node

                for i,item in enumerate(parts):
                    #print('\t\t Recursively call on ',item)

                    # get the ouput node
                    if i == len(parts)-1: # last node
                        output = end_node # so output is the actual output node
                    else:
                        output = graph.add_node() # for ever other node just create a new node

                    # recursively call the function with the item
                    if '()' in item:
                        # if item is brackets then get the contents from brck_conts
                        # The regex is our empty bracket notation so we pop the contents from brckt_conts list
                        # first in first out so take from the start
                        item = item.replace('()', '('+brckt_conts.pop(0)+')')
                    
                    
                    regex_to_NFA(item, graph, prev_output, output)

                    # update prev_output
                    prev_output = output
                        

# define a little function that creates an NFA given a regex expression
# used for testing purposes

def getNFA(regex):
    x = Graph()
    inputn = x.add_node()
    outputn = x.add_node()
    regex_to_NFA(regex, x, inputn, outputn)
    return x

#-----------------------------------------------------------------------------------------------------------#

# Now we should turn our NFA into a DFA
# Then reduce the DFA into a minimal DFA

# Define a function epsilon_closure that returns the epsilon closure of list of points in a graph
def epsilon_closure(graph, points):
    
    # for each point in set_points get all the epsilon connections and add them to new_points
    # Create a new set to be filled with connected points + original points
    new_points = set(points)

    for point in points:
        for conn in graph.get_neighbours(point, EPSILON):
            new_points.add(conn)
        
    # Now define a recursive base case
    if new_points == points:
        # There are no new points to be found so we have our solution
        return new_points
    else:
        # Otherwise recursively call the function with the new points
        return epsilon_closure(graph, new_points)

def move(points, NFA, value):
    # Given a set of possible points compute the next set of possible points
    # for a traversal value
    new_points = set()
    for point in points:
        for conn in NFA.get_neighbours(point, value):
            new_points.add(conn)
    return new_points


def NFA_to_DFA(DFA, NFA, NFA_input_node):
    
    # The algorithm to create a DFA from an NFA involves traversing every path on the NFA at once
    # taking the epsilon-closure at every stage.
    # Example
    # Starting with {0} the input node, take the epsilon-closure({0})
    # Then for each character in the language calculate the set of points that can be reached
    # Then take the epsilon closure of that and so on

    # For each set of possible NFA positions create a DFA node referenced by a dictionary
    # Dict:           set of NFA points       ---> DFA node
    #            set_hash x where x is a set  --->   int
    # Since sets are not hashable we define a function set_hash to turn them into unique hashable tuples

    set_hash = lambda x: tuple(sorted(list(x)))

    DFA_nodes = {}

    # Create a stack of NFA possiblilities to compute further from
    # Implement with a set of tuple(set())'s
    # For every element in here, elm, tuple(elm) will be in DFA_nodes
    compute_stack = set()


    # We start with the input node to the NFA and its epsilon-closure
    DFA_in = epsilon_closure(NFA, {NFA_input_node})
    # Add it to the computation stack
    compute_stack.add(set_hash(DFA_in))
    # create a DFA node for the current NFA possibility
    DFA_in_node = DFA.add_node()
    # and add this node to the DFA node dictionary
    DFA_nodes[set_hash(DFA_in)] = DFA_in_node


    while len(compute_stack) != 0: # While the computation stack is not empty

        # get a random possibility to compute its links
        current_DFA_pos = set(compute_stack.pop())

        # get the assigned node from the dict
        current_DFA_node = DFA_nodes[set_hash(current_DFA_pos)]

        #print('\nWe calculating with DFA_node ',current_DFA_node)

        # For each of the characters in the character set calculate a possible NFA state
        for character in character_set:

            new_pos = epsilon_closure(NFA, move(current_DFA_pos, NFA, character))

            if not new_pos == set(): # If the set is non empty
                new_pos_tup = set_hash(new_pos)
                if DFA_nodes.get(new_pos_tup, None) is None:
                    #print('_'+character+'_', end='')
                    # This possibility has never been seen before
                    # Create a new DFA node to refer to it
                    new_node = DFA.add_node()
                    # and add it to the dictionary
                    DFA_nodes[new_pos_tup] = new_node

                    print(new_node, end='')

                    # Now connect it to the node it was connected to
                    DFA.add_edge(current_DFA_node, new_node, character)

                    # Now add it to the computation stack so that its connections can be computed
                    compute_stack.add(new_pos_tup)
                else:
                    #print(character, end='')
                    # This node has been seen before so simply add a connection to it
                    # Get the posibility that it points to by DFA_nodes
                    points_to = DFA_nodes[new_pos_tup]
                    DFA.add_edge(current_DFA_node, points_to, character)


    return DFA_nodes





#-----------------------------------------------------------------------------------------------------------#
                 

if __name__=='__main__':
    # Create the NFA graph
    NFA = Graph()

    input_node = NFA.add_node()
    
    for expression in language:
        print('Computing the NFA for',expression['regex'])
        cur_output_node = NFA.add_node()
        expression['output_node'] = cur_output_node
        regex = expression['regex']
        regex_to_NFA(regex, NFA, input_node, cur_output_node)

    DFA = Graph()

    print('NFA to DFA...')
    print('Creating DFA nodes')
    w = NFA_to_DFA(DFA, NFA, input_node)
    print('')

    
    