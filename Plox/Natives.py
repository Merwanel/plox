from __future__ import annotations

from Plox.Environment import Environment
from Plox.LoxCallable import LoxCallable
import Plox.LoxInstance as LoxInstance
import Plox.AstInterpreter as AstInterpreter 
from Plox.Token import Token 
import time


class clock(LoxCallable) :
		@staticmethod
		def arity() -> int:
			return 0

		@staticmethod
		def call(*args, **kwargs) -> int :
			return time.time()

		@staticmethod
		def toString() -> str:
			return "<native fn clock>"
		
class LoxArrayGet(LoxCallable) :
		def __init__(self, elements: list[object]) -> None:
				self.elements = elements
		def arity(self) -> int:
				return 1
		def call(self,interpreter=None, arguments=...):
				index: int = int(arguments[0])
				return self.elements[index]
		def toString(self) -> str:
			return "<native fn get of Array>"
			
class LoxArraySet(LoxCallable) :
		def __init__(self, elements: list[object]) -> None:
				self.elements = elements
		def arity(self) -> int:
				return 2
		def call(self,interpreter=None, arguments=...):
				index: int = int(arguments[0])
				value: object = arguments[1]
				self.elements[index] = value
				return value
		def toString(self) -> str:
			return "<native fn set of Array>"
			
class LoxArray(LoxInstance.LoxInstance) :
	def __init__(self, size: int) -> None:
		super().__init__(None)
		self.elements = [None] * int(size)

	def get(self, token : Token) -> object :
		if token.lexeme == "get" :
			return LoxArrayGet(self.elements)
		elif token.lexeme == "set" :
			return LoxArraySet(self.elements)
		elif token.lexeme == "length" :
			return len(self.elements)
	
		raise RuntimeError(token, "Undefined property '" + token.lexeme + "'.")
	
	def set(self, token: Token, value: object):
		raise RuntimeError(token, "Can't add properties to arrays.")

	def toString(self) -> str :
		return str(self.elements)
	
	def __eq__(self, value: LoxArray) -> bool:
			return self.elements == value.elements


class LoxArrayFactory(LoxCallable) :   
	def arity(self) -> int:
		return 1
	
	def call(self, interpreter: AstInterpreter.AstInterpreter=None, arguments: list[object]=...):
		size = arguments[0]
		return LoxArray(size)
	
	def toString(self) -> str:
		 pass  
	
globals = Environment()
globals.define('clock', clock())
globals.define("Array", LoxArrayFactory())