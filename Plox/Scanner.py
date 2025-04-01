
from Plox.ErrorHandling import ErrorHandling
from Plox.Token import Token
from Plox.Const import *


class Scanner :
    """
    Produce tokens out of the source code
    """
    def __init__(self, error_handler :ErrorHandling) -> None:
        self.tokens : list[Token] = []
        self.error_handler = error_handler

    def is_valid_character(self, c:str) -> bool :
        return c in LEXEME_TO_TOKEN_1CHAR or c in LEXEME_TO_TOKEN or self.is_string(c) or c == '_'

    def is_string(self,c:str) -> bool :
        return ord('a') <= ord(c.lower()) <= ord('z')

    def scan(self, i: int, line: str) -> None :
        if self.tokens and self.tokens[-1].type =='EOF' :
            self.tokens.pop()
        token = Token()
        last_slash = float('inf')
        for col, c in enumerate(line) :
            if token.type == 'IDENTIFIER' and (self.is_string(c) or c.isdigit() or c == '_'):
                token.lexeme += c
                continue
            if token.type == 'IDENTIFIER':
                if token.lexeme in RESERVED_KEYWORD :
                    token.type = token.lexeme.upper()
                self.tokens.append(token)
                token = Token()
            if token.type == 'NUMBER' and not c.isdigit() and c != '.' or (c == '.' and '.' in token.lexeme) :
                has_end_dot = False
                if token.lexeme[-1] == '.' :
                    has_end_dot = True
                    token.lexeme = token.lexeme[:-1]
                token.literal = token.lexeme
                if '.' not in  token.lexeme :
                    token.literal += '.0'
                else :
                    pos_cut_off = len(token.literal) - 1
                    for i in range(len(token.literal)-1, -1, -1) :
                        if token.literal[i] == '.' or token.literal[i] != '0':
                            pos_cut_off = max(pos_cut_off, i+1)
                            break
                        pos_cut_off = i

                        token.literal = token.literal[:pos_cut_off+1]
                token.literal = float(token.literal)
                self.tokens.append(token)
                if has_end_dot :
                    self.tokens.append(Token('DOT', '.'))
                token = Token()
            if c == '"' :
                if token.type == 'STRING' :
                    self.tokens.append(token)
                    token = Token()
                else :
                    token.type = 'STRING'
                    token.literal=''
                continue
            if token.type == 'STRING'  :
                token.lexeme += c
                token.literal += c            
                continue
            if token.type == 'STRING':
                self.tokens.append(token)
                token = Token()

            if c.isdigit() or (token.type == 'NUMBER' and c == '.') :
                if token.type and token.type != 'NUMBER' :
                    self.tokens.append(token)
                    token = Token()
                token.type = 'NUMBER'
                token.lexeme += c
                continue


            if c in (' ', '\t', '\n') :
                if token.type == 'STRING' and c == ' ' :
                    token.lexeme += c
                    token.literal += c
                elif token.type != '' :
                    self.tokens.append(token)
                    token = Token()
                continue
            if c == '/' :
                if last_slash +1 == col :
                    token.type = ''
                    break
                last_slash = col
            if not self.is_valid_character(c) :
                self.error_handler.error('scanner', i, token, c)

            if c in LEXEME_TO_TOKEN:
                token_name = LEXEME_TO_TOKEN[c]
                if token.type != '' and f"{token.type}_{token_name}" not in VALID_TOKEN_COMBO :
                    self.tokens.append(token)
                    token = Token()
                if token.type :
                    token.type += '_'
                token.type += token_name
                token.lexeme += c

            elif token.type not in ('', 'STRING')  :
                self.tokens.append(token)
                token = Token()

            if c in LEXEME_TO_TOKEN_1CHAR :
                self.tokens.append(Token(LEXEME_TO_TOKEN_1CHAR[c], c))

            if token.type == '' and c not in LEXEME_TO_TOKEN_1CHAR and c not in LEXEME_TO_TOKEN and (self.is_string(c) or c.isdigit() or c == '_') :
                token.type = 'IDENTIFIER'
                token.lexeme = c
        if token.type != '' :
            if token.type == 'IDENTIFIER':
                if token.lexeme in RESERVED_KEYWORD :
                    token.type = token.lexeme.upper()
                self.tokens.append(token)
            elif token.type == 'STRING' :
                self.error_handler.error('scanner', i, token, c)
            elif token.type == 'NUMBER' :
                has_end_dot = False
                if token.lexeme[-1] == '.' :
                    has_end_dot = True
                    token.lexeme = token.lexeme[:-1]
                token.literal = token.lexeme
                if '.' not in  token.lexeme :
                    token.literal += '.0'
                else :
                    pos_cut_off = len(token.literal) - 1
                    for i in range(len(token.literal)-1, -1, -1) :
                        if token.literal[i] == '.' or token.literal[i] != '0':
                            pos_cut_off = max(pos_cut_off, i+1)
                            break
                        pos_cut_off = i

                        token.literal = token.literal[:pos_cut_off+1]
                token.literal = float(token.literal)
                self.tokens.append(token)
                if has_end_dot :
                    self.tokens.append(Token('DOT', '.'))
            else :
                self.tokens.append(token)
            token = Token()
        self.tokens.append(Token('EOF'))
