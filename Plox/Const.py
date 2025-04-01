LEXEME_TO_TOKEN_1CHAR = {
    '(':'LEFT_PAREN',
    ')':'RIGHT_PAREN',
    '{':'LEFT_BRACE',
    '}':'RIGHT_BRACE',
    ',':'COMMA',
    '.':'DOT',
    '-':'MINUS',
    '+':'PLUS',
    ';':'SEMICOLON',
    '*':'STAR',
}
LEXEME_TO_TOKEN = {
    '=':'EQUAL',
    '!':'BANG',
    '>':'GREATER',
    '<':'LESS',
    '/':'SLASH'
}
VALID_TOKEN_COMBO = ['EQUAL_EQUAL', 'BANG_EQUAL', 'GREATER_EQUAL' ,'LESS_EQUAL']

RESERVED_KEYWORD = [ 'and', 'class', 'else', 'false', 'for', 'fun', 'if', 'None', 'or', 'print', 'return', 'super', 'this', 'true', 'var', 'while']