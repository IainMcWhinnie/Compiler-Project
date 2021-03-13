import sys, os
import parsers, tokenize

filename = sys.argv[1]
rootname = filename.split('.')[0]


token_generator = tokenize.tokengenerator(filename)
abstract_tree = parsers.parse_program(token_generator)
code = abstract_tree.generate_code()



with open(rootname+'.asm', 'w') as f:
    f.write(code)



os.system('compile '+rootname)