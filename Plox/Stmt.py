from __future__ import annotations
from abc import ABC, abstractmethod
from Plox.Expr import Expr, Variable
from Plox.Token import Token

class Stmt(ABC) :
	"""unit designed to perform a side-effect"""
	@abstractmethod
	def accept(self, visitor: Visitor)  :
		 pass
	 
class Function(Stmt) : 
	def __init__(self, token: Token, params: list[Token], body: list[Stmt]) :
		self.token = token
		self.params = params
		self.body = body

	def accept(self, visitor: Visitor) :
		return visitor.visitFunctionStmt(self)
		
class Expression(Stmt) :
		def __init__(self, expression: Expr) :
			self.expression = expression

		def accept(self, visitor: Visitor) :
			return visitor.visitExpressionStmt(self)
		
class If(Stmt) :
	def __init__(self, condition: Expr, thenBranch: Stmt, elseBranch: Stmt) -> None:
			self.condition = condition 
			self.thenBranch = thenBranch
			self.elseBranch = elseBranch
		
	def accept(self, visitor: Visitor) :
			return visitor.visitIfStmt(self)
		
class While (Stmt):
	def __init__(self, condition: Expr, body: Stmt) :
		self.condition = condition
		self.body = body
	def accept(self, visitor: Visitor) :
			return visitor.visitWhileStmt(self)
		
	
class Print(Stmt) :
		def __init__(self, expression: Expr) :
			self.expression = expression

		def accept(self, visitor: Visitor) :
			return visitor.visitPrintStmt(self)
		
class Return(Stmt) :
	def __init__(self, keyword: Token, value: Expr) :
		self.keyword = keyword
		self.value = value
	def accept(self, visitor: Visitor) :
		return visitor.visitReturnStmt(self)
		
class Block(Stmt) :
		def __init__(self, statements: list[Stmt]) :
			self.statements = statements

		def accept(self, visitor: Visitor) :
			return visitor.visitBlockStmt(self)
		
class Class(Stmt) :
		def __init__(self,  token: Token , methods: list[Function], superClass : Variable = None) :
			self.token = token
			self.superClass = superClass
			self.methods = methods

		def accept(self, visitor: Visitor) :
			return visitor.visitClassStmt(self)
		
class Var(Stmt) :
		def __init__(self, token: Token, initializer: Expr) :
			self.token = token
			self.initializer = initializer

		def accept(self, visitor: Visitor) :
			return visitor.visitVarStmt(self)
			
class Visitor(ABC) :
		@abstractmethod
		def visitBlockStmt(self, stmt: Block):
			pass
		@abstractmethod
		def visitClassStmt(self, stmt: Class):
			pass
		@abstractmethod
		def visitExpressionStmt(self, stmt: Expression):
			pass
		@abstractmethod
		def visitFunctionStmt(self, stmt: Function):
			pass
		@abstractmethod
		def visitIfStmt(self, stmt: If):
			pass
		@abstractmethod
		def visitPrintStmt(self, stmt: Print):
			pass
		@abstractmethod
		def visitVarStmt(self, stmt: Var):
			pass
		@abstractmethod
		def visitReturnStmt(self, stmt: Return):
			pass
		@abstractmethod
		def visitWhileStmt(self, stmt: While):
			pass