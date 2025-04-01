from abc import ABC, abstractmethod

class LoxCallable(ABC) :
	
	@abstractmethod
	def arity() -> int:
		pass
	@abstractmethod
	def call(interpreter=None, arguments=[]) :
		pass
	@abstractmethod
	def toString() -> str:
		pass
