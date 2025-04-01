
from Plox.ErrorHandling import ErrorHandling
from Plox.Scanner import Scanner
from Plox.Parser import Parser
from Plox.AstInterpreter import AstInterpreter
from Plox.AstResolver import AstResolver
from Plox.Natives import globals
import Plox.Expr as Expr


class Plox :
    """ The plox interpreter, a tree-walk interpreter """
    def __init__(self, is_a_test=False) -> None :
        self.error_handler = ErrorHandling()
        self.scanner = Scanner(self.error_handler)
        self.parser = Parser(self.error_handler, self.scanner)
        
        self.locals: dict[Expr.Expr, int] = dict()
        """Map a variable name to how far the scope refered to is, to avoid shadowing problems"""
        
        self.astResolver = AstResolver(self.error_handler, self.locals)
        self.astInterpreter = AstInterpreter(error_handler=self.error_handler, locals=self.locals, env=globals, is_a_test=is_a_test)