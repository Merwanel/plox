import Plox.Expr as Expr
import Plox.Stmt as Stmt

class AstPrinter(Expr.Visitor) :
	"""
	Produce a string representation of a syntax tree
	"""
	def stringfyTree(self, statements: list[Stmt.Expression] | list[Stmt.Stmt] | Stmt.Expression | Expr.Expr) :
		if type(statements) != type([]) : 
			return statements.accept(self) if 'accept' in dir(statements) else statements 
		return [statement.accept(self) if 'accept' in dir(statement) else statement for statement in statements]
	
	def visitBinary(self, expr : Expr.Binary) :
		return f"(binary {expr.operator.lexeme} {self.stringfyTree(expr.left)} {self.stringfyTree(expr.right)})"
	
	def visitCall(self, expr : Expr.Call) :
		return f"(call {self.stringfyTree(expr.callee)} {self.stringfyTree(expr.arguments)})"
	
	def visitLogicalExpr(self, expr : Expr.Logical) :
		return f"(Logical {expr.operator.lexeme} {self.stringfyTree(expr.left)} {self.stringfyTree(expr.right)})"
	
	def visitLiteral(self, expr : Expr.Literal) :    
		return f"literal {expr.value}"
	
	def visitUnary(self, expr : Expr.Unary) :
		return f"(Unary {expr.operator.lexeme} {self.stringfyTree(expr.right)})"
	
	def visitSuper(self, expr : Expr.Super) :
		return f"(keyword: {expr.keyword} method: {expr.method})"
	
	def visitThis(self, expr : Expr.This) :
		return f"(keyword: {expr.keyword})"
	
	def visitSet(self, expr : Expr.Set) :
		return f"(set {self.stringfyTree(expr.object)} token: {expr.token} value: {self.stringfyTree(expr.value)})"
	
	def visitGet(self, expr : Expr.Get) :
		return f"(get {self.stringfyTree(expr.object)} token: {expr.token})"
		
	def visitGrouping(self, expr : Expr.Grouping) :
		return f"(group {self.stringfyTree(expr.expression)})"
		
	def visitVariableExpr(self, expr : Expr.Variable) :
		return f"(varexpr {expr.token.lexeme})"
	
	def visitAssignExpr(self, expr: Expr.Assign) :
		return f"(assign {expr.token.lexeme} to {self.stringfyTree(expr.expr)} )"
	
	def visitFunctionStmt(self, stmt: Stmt.Function) :
		return f"(function {stmt.token.lexeme} {self.stringfyTree(stmt.params)} {self.stringfyTree(stmt.body)} )"
	
	def visitExpressionStmt(self, stmt : Stmt.Expression) :
		return f"(statement {self.stringfyTree(stmt.expression)})"
	
	def visitIfStmt(self, stmt : Stmt.If) :
		return f"(If {self.stringfyTree(stmt.condition)} then {self.stringfyTree(stmt.thenBranch)} else {self.stringfyTree(stmt.elseBranch)})"
	
	def visitWhileStmt(self, stmt : Stmt.While) :
		return f"(while ({self.stringfyTree(stmt.condition)}) body :{self.stringfyTree(stmt.body)})"
	
	def visitReturnStmt(self, stmt : Stmt.Return) :
		return f"return keyword: {self.stringfyTree(stmt.keyword)} value:{self.stringfyTree(stmt.value)}"
		
	def visitPrintStmt(self, stmt : Stmt.Print) :
		return f"(print {self.stringfyTree(stmt.expression)})" 
	
	def visitClassStmt(self, stmt: Stmt.Class):
		return f"(class {stmt.token} superclass: {self.stringfyTree(stmt.superClass)} methods: {self.stringfyTree(stmt.methods)})" 
	
	def visitBlockStmt(self, stmt: Stmt.Block):
		return f"(block {self.stringfyTree(stmt.statements)})" 
	
	def visitVarStmt(self, stmt: Stmt.Var) :
		return f"(Var => lexeme:{stmt.token.lexeme} initializer:{self.stringfyTree(stmt.initializer) if stmt.initializer else None})" 
