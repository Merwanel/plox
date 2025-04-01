from __future__ import annotations
import Plox.Expr as Expr 
import Plox.Stmt as Stmt
from Plox.Environment import Environment
from Plox.Natives import globals
from Plox.LoxCallable import LoxCallable
from Plox.LoxFunction import LoxFunction
from Plox.LoxClass import LoxClass 
from Plox.LoxInstance import LoxInstance
from Plox.Return import Return
from Plox.Token import Token

from Plox.ErrorHandling import ErrorHandling

class AstInterpreter(Expr.Visitor, Stmt.Visitor) :
	"""
 	Walk the tree to interpret each node
  	"""
	def __init__(self, error_handler :ErrorHandling, locals: dict[Expr.Expr, int], env=Environment(), is_a_test=False) -> None:
		self.env = env
		self.error_handler = error_handler
		self.locals = locals
		self.is_a_test = is_a_test
		self.printed : list[str] = []
		
	def interpret(self, statements: list[Stmt.Stmt] | Expr.Expr) :
		try :
			if type(statements) == list :
					for statement in statements :
						self.execute(statement)
			else :
				return self.evaluate(statements)
		except Exception as e :
			self.error_handler.error(ori='astInterpreter', message=e)
						
	def executeBlock(self, statements: list[Stmt.Stmt], env: Environment) :
		previous = self.env
		try :
			self.env = env
			
			for statement in statements :
				self.execute(statement)
		finally :
			self.env = previous
	
	def execute(self, stmt: Stmt.Expression) :
		return stmt.accept(self)
	
	def evaluate(self, expr: Expr.Expr | Stmt.Expression) -> object:
		tmp = expr.accept(self)
		return tmp
	# Expressions
	
	def visitBinary(self, expr : Expr.Binary) :
		left = self.evaluate(expr.left)
		right = self.evaluate(expr.right)
		if expr.operator.type == 'PLUS' :
			return left + right
		if expr.operator.type == 'MINUS' :
			return left - right
		if expr.operator.type == 'STAR' :
			return left * right
		if expr.operator.type == 'SLASH' :
			return left / right
		if expr.operator.type == 'GREATER' :
			return left > right
		if expr.operator.type == 'GREATER_EQUAL' :
			return left >= right
		if expr.operator.type == 'LESS' :
			return left < right
		if expr.operator.type == 'LESS_EQUAL' :
			return left <= right
		if expr.operator.type == 'EQUAL_EQUAL' :
			return left == right
		if expr.operator.type == 'BANG_EQUAL' :
			return left != right
		return None
	
	def visitLogicalExpr(self, expr : Expr.Logical) :
		"""With a dimnamiccaly typed language , we just return the object 
		, then their truthiness will be evaluated"""
		left = self.evaluate(expr.left)
		if expr.operator.type == 'OR' and self.isTruthy(left) :
			return left
		if expr.operator.type == 'AND' and not self.isTruthy(left) :
			return left

		return self.evaluate(expr.right) 
	
	def visitLiteral(self, expr : Expr.Literal) :
		return expr.value 
	
	def visitUnary(self, expr : Expr.Unary) :
		right = self.evaluate(expr.right)
		if expr.operator.type == 'MINUS' :
			return -right
		if expr.operator.type == 'BANG' :
			return -self.isTruthy(right)
		return None
	
	def isTruthy(self, object: any) -> bool:
		if object == None :
			return False
		if type(object) == type(True) :
			return object
		return True
	
	def visitCall(self, expr : Expr.Call) :  
		callee: LoxCallable = self.evaluate(expr.callee)
		arguments = []
		for argument in expr.arguments :      
			arguments.append(self.evaluate(argument))
			
		function : LoxCallable  = callee

		if len(arguments) != function.arity() :
			raise RuntimeError(expr.paren, f"Expected \
					{function.arity()} arguments but got \
					{len(arguments)} .")

		return function.call(self, arguments)
	
	def visitSuper(self, expr: Expr.Super):
		distance = self.locals[expr]
		superclass: LoxClass = self.env.getAt(distance, "super")
		obj: LoxInstance = self.env.getAt(distance - 1, "this")
		method = superclass.findMethod(expr.method.lexeme)  
		
		if method == None :
			raise RuntimeError(expr.method, "Undefined property '" + expr.method.lexeme + "'.")
		
		return method.bind(obj)
		
	def visitThis(self, expr: Expr.This) :
		return self.lookUpVariable(expr.keyword, expr)
	
	def visitGet(self, expr : Expr.Get) :
		object = self.evaluate(expr.object)
		
		if isinstance(object, LoxInstance) :
			return object.get(expr.token)
		
		raise RuntimeError(expr.token, "Only intances have properties.")
			
	def visitSet(self, expr : Expr.Set) :
		object = self.evaluate(expr.object)
		
		if not isinstance(object, LoxInstance) :
			raise RuntimeError(expr.token, "Only intances have fields.")
		value = self.evaluate(expr.value)
		object.set(expr.token, value)
		return value
			
	def visitGrouping(self, expr : Expr.Grouping) :
		return self.evaluate(expr.expression)
	
	def visitVariableExpr(self, expr : Expr.Variable) :
		tmp = self.lookUpVariable(expr.token, expr)
		return tmp
	
	def lookUpVariable(self, token : Token, expr: Expr.Expr) :
		distance = self.locals.get(expr, None)
		if distance != None :
			return self.env.getAt(distance, token.lexeme)
		else :
			return globals.get(token)
		
	def visitAssignExpr(self, expr: Expr.Assign) :
		value = self.evaluate(expr.expr)
		distance = self.locals.get(expr, None)
		if distance != None :
			self.env.assignAt(distance, expr.token, value)
		else :
			self.env.assign(expr.token, value)
		return value
	
	
	# Statements
	
	def visitFunctionStmt(self, stmt: Stmt.Function) :
		function = LoxFunction(stmt, self.env)
		self.env.define(stmt.token.lexeme, function)
		
		return None
	
	def visitExpressionStmt(self, stmt : Stmt.Expression) :
		self.evaluate(stmt.expression)
		return None
	
	def visitIfStmt(self, stmt: Stmt.If):
		if self.isTruthy(self.evaluate(stmt.condition)) :
			self.execute(stmt.thenBranch)
		elif stmt.elseBranch != None :
			self.execute(stmt.elseBranch)
		return None
	
	def visitWhileStmt(self, stmt: Stmt.While) :
		while self.isTruthy(self.evaluate(stmt.condition)) :
			self.execute(stmt.body)
		return None
	
	def visitReturnStmt(self, stmt: Stmt.Return) :
		value = None
		if stmt.value != None:
			value = self.evaluate(stmt.value)
		
		# raise to return stuff wherever in a function
		raise Return(value)
	
	def visitPrintStmt(self, stmt : Stmt.Print) :
		if self.is_a_test :
			self.printed.append(self.evaluate(stmt.expression))
		else :
			print(self.evaluate(stmt.expression))
		return None
	
	def visitBlockStmt(self, stmt: Stmt.Block):
		self.executeBlock(stmt.statements, Environment(enclosing=self.env))
		return None
	
	def visitClassStmt(self, stmt : Stmt.Class) :
		superClass = None
		
		if stmt.superClass != None :
			superClass = self.evaluate(stmt.superClass)
			if not isinstance(superClass, LoxClass) :
				raise RuntimeError("SuperClass must be a class")
		
		self.env.define(stmt.token.lexeme, None)
		
		if stmt.superClass != None :
			self.env = Environment(self.env)
			self.env.define("super", superClass)
		 
		methods : dict[str, LoxFunction] = dict()
		for method in stmt.methods :
			isInitializer = method.token.lexeme == 'this'
			methods[method.token.lexeme] = LoxFunction(method, self.env, isInitializer) 
			
		klass = LoxClass(stmt.token.lexeme, superClass, methods)
		
		if stmt.superClass != None :
			self.env = self.env.enclosing
			
		self.env.assign(stmt.token, klass)
			
		return None
		
	def visitVarStmt(self, stmt: Stmt.Var) :
		value = None
		if stmt.initializer != None :
			value = self.evaluate(stmt.initializer)
		self.env.define(stmt.token.lexeme, value)