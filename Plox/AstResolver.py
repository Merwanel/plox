from __future__ import annotations, absolute_import
from typing import Literal
import Plox.Expr as Expr 
import Plox.Stmt as Stmt
from Plox.Token import Token
from Plox.ErrorHandling import ErrorHandling

class AstResolver(Expr.Visitor, Stmt.Visitor) :
	"""
	Semantic analysis to figure out which Environment object should a variable name be looked at
	This way there is no variable shadowing of a closure after its definition  
  	"""
	def __init__(self, error_handler : ErrorHandling, locals: dict[Expr.Expr, int], is_a_test=False) -> None:
		self.error_handler = error_handler
		self.locals = locals
		self.is_a_test = is_a_test
		self.scopes : list[dict[str, bool]] = []  # [variable name :  True iff the variable is declared and defined]
		self.currentFunction: Literal[None , 'IS_FUNCTION', 'IS_METHOD', 'IS_INITIALIZER']  = None 
		self.currentClass: Literal[None, 'CLASS', 'SUBCLASS'] = None
		
		
	# Expressions
	
	def visitBinary(self, expr : Expr.Binary) :
		self.resolve(expr.left)
		self.resolve(expr.right)
		return None
	
	def visitLogicalExpr(self, expr : Expr.Logical) :
		self.resolve(expr.left)
		self.resolve(expr.right) 
		return None
	
	def visitLiteral(self, expr : Expr.Literal) :
		return None 
	
	def visitUnary(self, expr : Expr.Unary) :
		self.resolve(expr.right)
		return None
	
	def visitThis(self, expr: Expr.This):
		if self.currentClass == None :
			self.error_handler.error(ori='resolver', message=f"{expr.keyword.lexeme} Can't use 'this' outside of a class.")
			return None
		
		self.resolveLocal(expr, expr.keyword)
		return None
	
	def visitSuper(self, expr: Expr.Super):
		if self.currentClass == None :
			self.error_handler.error(ori='resolver',message= f"{expr.keyword.lexeme}, Can't use 'super' outside of a class.")
		elif self.currentClass != 'SUBCLASS' :
			self.error_handler.error(ori='resolver',message= f"{expr.keyword.lexeme}, Can't use 'super' in a class with no superclass.")
			
		self.resolveLocal(expr, expr.keyword)
		return None 
	
	def visitSet(self, expr : Expr.Set) :  
		self.resolve(expr.object)      
		self.resolve(expr.value)
		return None
	
	def visitCall(self, expr : Expr.Call) :  
		self.resolve(expr.callee)
		for argument in expr.arguments :      
			self.resolve(argument)
		return None
	
	def visitGet(self, expr: Expr.Get) :
		self.resolve(expr.object)
		return None

	def visitGrouping(self, expr : Expr.Grouping) :
		self.resolve(expr.expression)
		return None
	
	def visitVariableExpr(self, expr : Expr.Variable) :
		if self.scopes and self.scopes[-1].get(expr.token.lexeme, None) == False :
			self.error_handler.error(ori='resolver', message=f"{expr.token.lexeme} Can't read local variable in its own initializer.")
		self.resolveLocal(expr, expr.token)
		
	def resolveLocal(self, expr : Expr.Expr, token: Token) :
		"""Get the number of hops we have to jump to get the right environnement where the variable is stored"""
		for i in range(len(self.scopes)-1 , -1, -1) :
			if token.lexeme in self.scopes[i] :
				self.locals[expr] = len(self.scopes) - 1 - i
				return
		
	def visitAssignExpr(self, expr: Expr.Assign) :
		self.resolve(expr.expr)
		self.resolveLocal(expr, expr.token)
		return None
	
	
	# Statements
	
	def visitFunctionStmt(self, stmt: Stmt.Function) :
		self.declare(stmt.token)
		self.define(stmt.token)
		self.resolveFunction(stmt, 'IS_FUNCTION')
		return None
	
	def resolveFunction(self, stmt: Stmt.Function, type: Literal[None, 'IS_FUNCTION', 'IS_METHOD', 'IS_INITIALIZER']) :
		enclosingFunction = self.currentFunction
		self.currentFunction = type
		self.beginScope()

		for param in stmt.params :
			self.declare(param)
			self.define(param)
		self.resolve(stmt.body)
		self.endScope()
		self.currentFunction = enclosingFunction
		
	def visitExpressionStmt(self, stmt : Stmt.Expression) :
		self.resolve(stmt.expression)
		return None
	
	def visitIfStmt(self, stmt: Stmt.If):
		self.resolve(stmt.condition)
		self.resolve(stmt.thenBranch)
		if stmt.elseBranch != None :
			self.resolve(stmt.elseBranch)
		return None
	
	def visitWhileStmt(self, stmt: Stmt.While) :
		self.resolve(stmt.condition) 
		self.resolve(stmt.body)
		return None
	
	def visitReturnStmt(self, stmt: Stmt.Return) :
		if self.currentFunction == None :
			self.error_handler.error(ori='resolver', message=f"{stmt.keyword}, Can't return from top-level code.")
		if self.currentFunction == 'IS_INITIALIZER' :
			self.error_handler.error(ori='resolver', message=f"{stmt.keyword}, Can't return from an initializer.")
		if stmt.value != None:
			self.resolve(stmt.value)
		return None
	
	def visitPrintStmt(self, stmt : Stmt.Print) :
		self.resolve(stmt.expression)
		return None
	
	def visitBlockStmt(self, stmt: Stmt.Block):
		self.beginScope()
		self.resolve(stmt.statements)
		self.endScope()
		return None
	
	def visitClassStmt(self, stmt : Stmt.Class) :
		enclosingClass = self.currentClass
		self.currentClass = 'CLASS'
		
		self.declare(stmt.token)
		self.define(stmt.token)
		if stmt.superClass != None and stmt.superClass.token.lexeme == stmt.token.lexeme :
			self.error_handler.error(ori="resolver", message=f"{stmt.superClass.token.lexeme}, A class can't inherit from itself.")
		if stmt.superClass != None :
			self.currentClass = 'SUBCLASS'
			self.resolve(stmt.superClass)
		
		
		if stmt.superClass != None :
			self.beginScope()
			self.scopes[-1]["super"] = True
		
		self.beginScope()
		self.scopes[-1]["this"] = True
		
		for method in stmt.methods :
			type = 'IS_INITIALIZER' if method.token.lexeme == "init" else 'IS_METHOD'
			self.resolveFunction(method, type)
		
		self.endScope()
		
		
		if stmt.superClass != None :
			self.endScope()
		
		self.currentClass = enclosingClass
		return None
	
	def resolve(self, stmts: list[Stmt.Stmt] | Stmt.Stmt | Expr.Expr) :
		if  isinstance(stmts, Stmt.Stmt) :
			stmts.accept(self)
			return
		if  isinstance(stmts, Expr.Expr) :
			stmts.accept(self)
			return
		for stmt in stmts :
			stmt.accept(self)
			
	def beginScope(self) :
		self.scopes.append(dict())
	
	def endScope(self) :
		self.scopes.pop()  
	
	def visitVarStmt(self, stmt: Stmt.Var) :
		self.declare(stmt.token)
		if stmt.initializer != None:
			self.resolve(stmt.initializer)
		self.define(stmt.token)
		return None
	
	def declare(self, token: Token) :
		if not self.scopes :
			return
		if token.lexeme in self.scopes[-1] :
			self.error_handler.error(ori='resolver', message=f"Already a variable with the name {token.lexeme} in this scope")
		self.scopes[-1][token.lexeme] = False 
		
	def define(self, token: Token) :
		if not self.scopes : return
		self.scopes[-1][token.lexeme] = True