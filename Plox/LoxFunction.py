from __future__ import annotations
from Plox.LoxCallable import LoxCallable
import Plox.LoxInstance as LoxInstance
import Plox.Stmt as Stmt
import Plox.AstInterpreter
from Plox.Environment import Environment
from Plox.Return import Return

class LoxFunction(LoxCallable) :  
	def __init__(self, declaration: Stmt.Function, closure: Environment, isInitializer: bool = False) -> None:
		self.declaration = declaration
		self.closure = closure
		self.isInitializer = isInitializer
	
	def arity(self) -> int:
		return len(self.declaration.params)
	
	def call(self, interpreter : Plox.AstInterpreter.AstInterpreter=None, arguments=[]) :
		environment = Environment(enclosing=self.closure)
		for i in range(len(self.declaration.params)) :
			environment.define(self.declaration.params[i].lexeme, arguments[i])
		
		try: 
			interpreter.executeBlock(self.declaration.body, environment)
		except Return as returnVal :
			
			if self.isInitializer :
				# a empty return in a constructor will return its instance
				return self.closure.getAt(0, "this")
						
			return returnVal.value
		
		return None
	
	def bind(self, instance : LoxInstance) -> LoxFunction :
		env = Environment(self.closure)
		env.define("this", instance)
		return LoxFunction(self.declaration, env, self.isInitializer)
	
	def toString(self) -> str:
		return f"<fun {self.declaration.token.lexeme} >"
	
	def __repr__(self) -> str:
		return self.toString()