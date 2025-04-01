from __future__ import annotations, absolute_import
import Plox.LoxClass as LoxClass
from Plox.Token import Token

class LoxInstance :
	def __init__(self, klass: LoxClass.LoxClass) -> None :
		self.klass = klass
		self.fields : dict[str, object] = dict()

	def toString(self) -> str:
		if self.klass == None : 
			return "None instance"
		return self.klass.name + " instance"
	
	def __repr__(self) -> str:
		return self.toString()
	
	def get(self, token: Token) -> object :
		if token.lexeme in self.fields :
			return self.fields[token.lexeme]
		
		method = self.klass.findMethod(token.lexeme)
		if method != None :
			return method.bind(self)
		
		raise RuntimeError(token, f"Undefined Property '{token.lexeme}'")
	
	def set(self, token: Token, value : object) :
		self.fields[token.lexeme] = value