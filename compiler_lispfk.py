from getch import getche
from sidekick import opt
import click
import pprint
import ox

lexer = ox.make_lexer([
    ('COMMENT', r';(.)*'),
    ('NEW_LINE', r'\n+'),
    ('OPEN_BRACKET', r'\('),
    ('CLOSE_BRACKET', r'\)'),
    ('NAME', r'[a-zA-Z_][a-zA-Z_0-9-]*'),
    ('NUMBER', r'\d+(\.\d*)?'),
])

token_list = [
    'NAME',
    'NUMBER',
    'OPEN_BRACKET',
    'CLOSE_BRACKET',
]

identity = lambda x: x

parser = ox.make_parser([

    ('tuple : OPEN_BRACKET elements CLOSE_BRACKET', lambda a, x, b: x),
    ('tuple : OPEN_BRACKET CLOSE_BRACKET', lambda a, b: '[]'),
    ('elements : term elements', lambda x, xs: [x] + xs),
    ('elements : term', lambda x: [x]),
    ('term : atom', identity),
    ('term : tuple', identity),
    ('atom : NAME', identity),
    ('atom : NUMBER', lambda x: int(x)),

] , token_list)

data = [0]
ptr = 0
code_ptr = 0
breakpoints = []

@click.command()
@click.argument('source_file',type=click.File('r'))
@click.option('-o', nargs=1)
def build(o, source_file):

    output = '%s' % o
    print_ast = pprint.PrettyPrinter(width=60, compact=True)
    source = source_file.read()

    tokens = lexer(source)

    tokens = [value for value in tokens if str(value)[:7] \
        != 'COMMENT' and str(value)[:8] != 'NEW_LINE']
    ast = parser(tokens)

    #print_ast.pprint(ast)
    final_code = ''
    final_code = lf(ast, ptr, final_code)

    exit_arq = open('output.bf', 'w')
    exit_arq.write(final_code)
    exit_arq.close()

function_definition = {}

def lf(source, ptr, final_code):

    # variable to make sure that will jump def and while elements
    # for avoid repetition
    jump_elements = 0

    for command in source:

        if jump_elements == 0:

            if isinstance(command, list):
                final_code = lf(command, ptr, final_code)

            elif command == 'do-after':
                i = 0
                while i < len(source[2]):
                    lista = ['do', source[2][i], source[1]]
                    final_code = lf(lista, ptr, final_code)
                    i += 1

            elif command == 'do-before':
                i = 0
                while i < len(source[2]):
                    lista = ['do', source[1], source[2][i]]
                    final_code = lf(lista, ptr, final_code)
                    i += 1

            elif command == 'loop':
                final_code = final_code + '['
                final_code = lf(source[1:len(source)], ptr, final_code)

                jump_elements = len(source)
                final_code = final_code + ']'

            elif command == 'def':
                function_definition[source[1]] = [source[2], source[3]]
                jump_elements = len(source)

            elif command == 'add':
                final_code = add_func(int(source[1]), final_code)

            elif command == 'sub':
                final_code = sub_func(int(source[1]), final_code)

            elif command == 'inc':
                final_code = final_code + '+'

            elif command == 'dec':
                final_code = final_code + '-'

            elif command == 'right':
                final_code = final_code + '>'

            elif command == 'left':
                final_code = final_code + '<'

            elif command == 'print':
                final_code = final_code + '.'

            elif command == 'read':
                final_code = final_code + ','

            elif command in function_definition:
                lista = function_definition[command][1]
                final_code = lf(lista, ptr, final_code)

        else:
            jump_elements -= 1

    return final_code

def add_func(qt,final_code):
    for it in range(0,qt):
        final_code = final_code + '+'
    return final_code

def sub_func(qt, final_code):
    for it in range(0,qt):
        final_code = final_code + '-'
    return final_code

if __name__ == '__main__':
    build()
