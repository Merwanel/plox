from typing import Literal
import sys
from Plox.Token import Token

class ErrorHandling :
	def __init__(self) -> None:
			self.has_lexical_errors = False
			self.lexical_errors = []
			self.parser_errors = []
			self.resolver_errors = []
			self.astInterpreter_errors = []

	def error(self, ori : Literal['scanner','parser', 'resolver'] ,*args, **kwargs) :
		if ori == 'scanner' :
				self.error_scanning(*args, **kwargs)
		if ori == 'parser' :
				self.error_parsing(*args, **kwargs)
		if ori == 'resolver' :
				self.error_resolver(*args, **kwargs)
		if ori == 'astInterpreter' :
				self.error_astInterpreter(*args, **kwargs)
	
	def error_scanning(self, i : int, token: Token, c='') :
			self.has_lexical_errors = True
			if token.type == 'STRING' :
					message = f"[line {i+1}] Error: Unterminated string."
			else :
					message = f"[line {i+1}] Error: Unexpected character: {c}"
			print(message, file=sys.stderr)
			self.lexical_errors.append(message)
	
	def error_parsing(self, token: Token, message: str) :
		if (token.type == 'EOF') :
			message = f"{token.line} at end, " + message
		else :
			message = f"{token.line}, at {token.lexeme} , " + message
		print(message, file=sys.stderr)
		self.parser_errors.append(message)
		
	def error_resolver(self, message : str) :
		print(message, file=sys.stderr)
		self.resolver_errors.append(message)
		
	def error_astInterpreter(self, message : str) :
		print(message, file=sys.stderr)
		self.astInterpreter_errors.append(message)
		
		