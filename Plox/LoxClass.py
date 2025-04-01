from __future__ import annotations, absolute_import
from Plox.LoxCallable import LoxCallable
import Plox.LoxInstance as LoxInstance
import Plox.LoxFunction as LoxFunction 

class LoxClass(LoxCallable) :
	def __init__(self, name : str, superClass: LoxClass, methods : dict[str, LoxFunction.LoxFunction]) -> None:
		self.name = name
		self.superClass = superClass
		self.methods = methods
	
	def arity(self) -> int:
		initializer = self.findMethod("init")
		return initializer.arity() if initializer != None  else 0
	
	def call(self, interpreter=None, arguments=[]) :
		instance = LoxInstance.LoxInstance(self)
		initializer = self.findMethod("init")
		if initializer != None :
			initializer.bind(instance).call(interpreter, arguments)
		return instance
	
	def findMethod(self, name: str) :
		if name in self.methods :
			return self.methods[name]
		if self.superClass != None :
			return self.superClass.findMethod(name)
		
		return None
	
	def toString(self) :
		superClass_str = '< ' + str(self.superClass) if self.superClass != None else ''
		return self.name + superClass_str
	
	def __repr__(self) -> str:
		return self.toString()