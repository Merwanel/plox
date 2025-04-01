from __future__ import annotations
from Plox.Token import Token

class Environment :
	"""
	An object which holds all the variables of a scope and a pointer toward its nearest outer scope
	"""
	def __init__(self, enclosing: Environment = None) -> None:
		self.values: dict[str,any] = dict()
		self.enclosing = enclosing
	
	def define(self, name: str, value: any) :
		self.values[name] = value    
		
	def assign(self, token: Token, value: any) :
		env = self
		while env :
			if token.lexeme in env.values :
				env.values[token.lexeme] = value
				return
			env = env.enclosing

		raise  RuntimeError(token, f"Undefined variable ' {token.lexeme} '.")
	
	def assignAt(self, distance: int, token: Token, value) -> None :
		self.ancestor(distance).values[token.lexeme] = value
		
	def get(self, token: Token) :
		env = self
		while env :
			if token.lexeme in env.values :
				return env.values[token.lexeme]
			env = env.enclosing

		raise  RuntimeError(token, f"Undefined variable ' {token.lexeme} '.")
	
	def getAt(self, distance: int, name: str) :
		return self.ancestor(distance).values[name]
	
	def ancestor(self, distance: int) -> Environment :
		env = self
		for _ in range(distance) :
			if not env.enclosing :
				raise Exception(f"{env} has no enclosing environment, the resolver must have made a mistake")
			env = env.enclosing
		return env
		
	def getAllEnv(self) :
		env = self
		ans = []
		while env :
			ans.append(env.values)
			env = env.enclosing
		return ans

		