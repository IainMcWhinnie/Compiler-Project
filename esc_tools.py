################################################# Tools.py ##################################################

# Define some functions and tools that are useful for our python when dealing with defining escaped characters 


#-----------------------------------------------------------------------------------------------------------#


def replace_with_esc(string, target, new):
    # init a new string and a boolean for escapement
    new_string = '' 
    escape = False

    # for each character
    for char in string:

        if escape: # if the character is escaped simply add it to the string regardless and turn escape off
            new_string += char
            escape = False

        elif char == '\\': # if character is an unescaped backslash then set escape to true and add to string
            escape = True
            new_string += '\\'

        else: # otherwise as long as the character isnt the target to remove then add it
            if char != target:
                new_string += char

    return new_string



def split_with_esc(string, seperator):
    options = [] # set up the empty list
    current_string = '' # a buffer string that is added to as we iterate along the string and
    # peridically saved to options and reset
    escape = False # escapement boolean

    # for each character in the string
    for char in string:
        if escape: # If the character is escaped simply add it to the current string and turn off escape
            current_string += char
            escape = False

        elif char == '\\': # if the escapement character turn on escape and add the character to the string
            # Note escape = false because of the if/elif statement
            current_string += char
            escape = True

        elif char == seperator: # If the character is the dividing character then
            options.append(current_string) # add the previous current_string
            current_string = '' # and reset current string

        else: # unescaped normal character
            current_string += char


    options.append(current_string) # add the last option which the for loop doesnt catch
    return options


def find_with_esc(string, target, start=0, end=None):
    if end is None:
        end = len(string)
    i = string.find(target, start, end) # find the first target
    while i > 0 and string[i-1] == '\\': # if the character is escaped
        i = string.find(target, i+1) # try again

    return i

def rfind_with_esc(string, target, start=0, end=None):
    if end is None:
        end = len(string)
    i = string.rfind(target, start, end) # fin the last target
    while i > 0 and string[i-1] == '\\': # if the character is escaped
        i = string.rfind(target, 0, i) # try again

    return i