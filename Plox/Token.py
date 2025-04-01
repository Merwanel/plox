from __future__ import annotations

from Plox.Const import RESERVED_KEYWORD

class Token :
    """ 
    Elementary unit in the compiler
    Result of the scanning step
    """
    def __init__(self, type='', lexeme='', literal=None, line='') -> None:
        self.line = line
        """line where the token appeared"""
        
        self.type = type
        
        self.lexeme = lexeme
        """raw string from the source code"""
        
        self.literal = literal
        """value of the token"""

    def __repr__(self) -> str:
        if self.type == 'IDENTIFIER' and self.lexeme in RESERVED_KEYWORD :
            return f"{self.type} {self.lexeme} None"
        if self.type == 'STRING' :
            return f"{self.type} \"{self.lexeme}\" {self.lexeme}"
        return f"{self.type} {self.lexeme} {self.literal}"