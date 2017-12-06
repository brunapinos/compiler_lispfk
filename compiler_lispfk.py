from getch import getche
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
def build(source_file):

    print_ast = pprint.PrettyPrinter(width=60, compact=True)
    source = source_file.read()

    tokens = lexer(source)

    tokens = [value for value in tokens if str(value)[:7] != 'COMMENT' and str(value)[:8] != 'NEW_LINE']
    ast = parser(tokens)

    # print_ast.pprint(ast)
    lf(ast, ptr)

function_definition = {}

def lf(source, ptr):

    for command in source:

        if isinstance(command, list):
            lf(command, ptr)

        elif command == 'do-after':
            i = 0
            while i < len(source[2]):
                lista = ['do', source[1], source[2][i]]
                lf(lista, ptr)
                i += 1

        elif command == 'do-before':
            i = 0
            while i < len(source[2]):
                lista = ['do', source[2][i], source[1]]
                lf(lista, ptr)
                i += 1

        elif command == 'loop':
            while data[ptr] != 1:
                lf(source[1:len(source)], ptr)

        elif command == 'def':
            function_definition[source[1]] = [source[2], source[3]]

        elif command == 'add':
            data[ptr] = (data[ptr] + int(source[1])) % 256

        elif command == 'sub':
            data[ptr] = (data[ptr] - int(source[1])) % 256

        elif command == 'inc':
            data[ptr] = (data[ptr] + 1) % 256;

        elif command == 'dec':
            data[ptr] = (data[ptr] - 1) % 256;

        elif command == 'right':
            ptr += 1
            if ptr == len(data):
                data.append(0)

        elif command == 'left':
            ptr -= 1

        elif command == 'print':
            print(chr(data[ptr]), end='')

        elif command == 'read':
            data[ptr] = ord(getche())

        elif command in function_definition:
            lista = function_definition[command][1]
            lf(lista, ptr)


if __name__ == '__main__':
    build()
