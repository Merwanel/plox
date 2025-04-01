from Plox.Token import Token
import Plox.Expr as Expr
from Plox.Scanner import Scanner
from Plox.ErrorHandling import ErrorHandling
import Plox.Stmt as Stmt 

class Parser :
	""" 
	Build syntax trees from the scanned tokens
	Where Stmt and Expr objects are the nodes
 	Use a top-down approach for that ( Recursive Descent  )
	"""
	def __init__(self, error_handler :ErrorHandling, scanner :Scanner) -> None:
		self.error_handler = error_handler
		self.tokens = scanner.tokens
		self.i = 0
		
		self.statements : list[Stmt.Stmt]
		"""each element is a statement representing the root of a syntax tree"""
		
		# for REPL, if it has found one expression and only one then it will print it
		self.allowExpression = True  
		self.foundExpression = False
		
	def isAtEnd(self) :
		return self.i + 1 == len(self.tokens)
	
	def parseRepl(self) :
		self.allowExpression = True
		self.statements: list[Stmt.Stmt] = []
		while not self.isAtEnd() :
			self.statements.append(self.declaration())

			if self.foundExpression :
				last = self.statements[-1]
				if type(last) == type(Stmt.Expression(None)) : 
					return last.expression
				return None

			self.allowExpression = False

		return self.statements
		
	def parse(self) -> list[Stmt.Stmt]:
		self.statements: list[Stmt.Stmt] = []
		while not self.isAtEnd() :
			self.statements.append(self.declaration())
		return self.statements; 
	
	def declaration(self) : 
		"""
		declaration    → classDecl | funDecl | varDecl | statement ;
		"""   
		try :
			if self.match(['CLASS']) :
				self.advance()
				return self.classDecl()
			if self.match(['FUN']) :
				self.advance()
				return self.function('function')
			if self.match(['VAR']) :
				self.advance()
				return self.varDeclaration()
			return self.statement()
		except Exception as error : 
			print('EXCEPTION', error)
			self.synchronize()
			return None
	 
	def classDecl(self) :
		"""
		classDecl      → "class" IDENTIFIER ( "<" IDENTIFIER )? "{" function* "}" ;
		"""
		className = self.consume_or_raise(['IDENTIFIER'], "Expect a identifier after 'class'")
		superClass = None
		if self.match(['LESS']) :
			self.advance()
			superClass = Expr.Variable(self.consume_or_raise(['IDENTIFIER'], "Expect superclass name after '<'"))
			
		self.consume_or_raise(['LEFT_BRACE'], "Expect '{' for a class")
		methods : list[Stmt.Function] = []
		
		while not self.isAtEnd() and not self.match(['RIGHT_BRACE']) :
			methods.append(self.function('method'))
			
		self.consume_or_raise(['RIGHT_BRACE'], "Expect '}' at the end of a class")
		return Stmt.Class(className, methods, superClass)
	
	def function(self, kind: str) :
		"""
		funDecl        → "fun" function ;
		function       → IDENTIFIER "(" parameters? ")" block ;
		"""
		callee = self.consume_or_raise(['IDENTIFIER'], f"Expect {kind} name.")
		self.consume_or_raise(['LEFT_PAREN'], f"Expect an '(' after {kind} name")
		param = self.parameter() if not self.match(['RIGHT_PAREN']) else []
		self.consume_or_raise(['RIGHT_PAREN'], "Expect an ')' after the parameters")
		self.consume_or_raise(['LEFT_BRACE'], f"Expect an '{{' before  {kind} ")
		body = self.block()
		return Stmt.Function(callee, param, body)
		
	def parameter(self) :
		"""
		parameters     → IDENTIFIER ( "," IDENTIFIER )* ;
		"""
		params = [self.consume_or_raise(['IDENTIFIER'], "Expect an identifier as paramater")]
		while self.match(['COMMA']) :
			self.advance()
			params.append(self.consume_or_raise(['IDENTIFIER'], "Expect an identifier as paramater"))
		return params
	
	def varDeclaration(self) :
		"""
		varDecl        → "var" IDENTIFIER ( "=" expression )? ";" ;
		"""
		token = self.consume_or_raise(['IDENTIFIER'], "Expect variable name.");
		initializer: Expr = None
		if self.match(['EQUAL']) :
			self.advance()
			initializer = self.expression()

		self.consume_or_raise(['SEMICOLON'], "Expect ';' after variable declaration.")
		return Stmt.Var(token, initializer)
		
		
	def statement(self) :
		"""
		statement      → exprStmt | forStmt | ifStmt 
										| printStmt | returnStmt | whileStmt | block ;
		"""
		if self.match(['FOR']) :
			self.advance()
			return self.forStatement()
		if self.match(['IF']) :
			self.advance()
			return self.ifStatement()
		if self.match(['PRINT']) :
			self.advance()
			return self.printStatement()
		if self.match(['RETURN']) :
			self.advance()
			return self.returnStatement()
		if self.match(['WHILE']) :
			self.advance()
			return self.whileStatement()
		if self.match(['LEFT_BRACE']) :
			self.advance()
			return Stmt.Block(self.block())
		return self.expressionStatement()
	
	def forStatement(self) :
		"""
		forStmt        → "for" "(" ( varDecl | exprStmt | ";" )
								 expression? ";"
								 expression? ")" statement ;
		
		Desugaring to a While statement
		"""
		self.consume_or_raise(['LEFT_PAREN'], "Expect ( after 'for'")
		initializer : Stmt.Stmt = None
		if self.match(['SEMICOLON']) :
			self.advance()
			initializer = None
		elif self.match(['VAR']) :
			self.advance()
			initializer = self.varDeclaration()
		else :
			initializer = self.expressionStatement()
		
		condition: Expr.Expr = None
		if self.current().type != 'SEMICOLON' :
			condition = self.expression()
			
		self.consume_or_raise(['SEMICOLON'], "Expect ';' after loop condition.")
		increment: Stmt.Stmt = None
		if self.current().type != 'RIGHT_PAREN' :
			increment = self.expression()
			
		self.consume_or_raise(['RIGHT_PAREN'], "Expect ')' after for clauses.")
		
		body = self.statement()
		
		# desugaring :
		if increment != None :
			body = Stmt.Block([body, Stmt.Expression(increment)])
		
		if condition == None :
			condition = Expr.Literal(True)  # will create an infinite loop
		body = Stmt.While(condition, body)
		
		if initializer != None :
			body = Stmt.Block([initializer, body])

		return body
		
	def ifStatement(self) :
		"""
		ifStmt         → "if" "(" expression ")" statement  ( "else" statement )? ;
		"""
		self.consume_or_raise(['LEFT_PAREN'], "Expect '(' after 'if'.");
		condition = self.expression()
		self.consume_or_raise(['RIGHT_PAREN'], "Expect ')' after if condition."); 
		thenBranch = self.statement()
		elseBranch = None
		if self.match(['ELSE']) :
			self.advance()
			elseBranch = self.statement()

		return Stmt.If(condition, thenBranch, elseBranch)
	
	def printStatement(self) :
		value = self.expression()
		self.consume_or_raise(['SEMICOLON'], "Expect ';' after value.")
		return Stmt.Print(value)
	
	def returnStatement(self) :
		"""
		returnStmt     → "return" expression? ";" ;
		"""    
		keyword = self.current()
		value = None
		if not self.match(['SEMICOLON']) :
			value = self.expression() 

		self.consume_or_raise(['SEMICOLON'], "Excpect ';' after return statement")
		return Stmt.Return(keyword, value)
	
	def whileStatement(self) :
		"""
		whileStmt      → "while" "(" expression ")" statement ;
		"""
		self.consume_or_raise(['LEFT_PAREN'], "Expect '(' after value.")
		expr = self.expression()
		self.consume_or_raise(['RIGHT_PAREN'], "Expect ')' after value.")
		stmt = self.statement()
		return Stmt.While(expr, stmt)
	
	def expressionStatement(self) :
		expr = self.expression()
		if self.allowExpression and self.isAtEnd() :
			self.foundExpression = True
		else :
			self.consume_or_raise(['SEMICOLON'], "Expect ';' after expression.")
		return Stmt.Expression(expr)
	
	def block(self) -> list[Stmt.Stmt] :
		"""
		block          → "{" declaration* "}" ;
		"""
		statements: list[Stmt.Stmt] = []
		while not self.match(['RIGHT_BRACE']) and not self.isAtEnd() :
			statements.append(self.declaration())
			
		self.consume_or_raise(['RIGHT_BRACE'], "Expect '}' after value.")
		return statements
	
	def current(self) -> Token :
		return self.tokens[self.i]
	
	def advance(self) :
		if not self.isAtEnd() :
			self.i += 1
			
	def current_and_advance(self) -> Token :
		res = self.current()
		self.advance()
		return res
	
	def peek(self) -> Token :
		if self.i == len(self.tokens) :
			return -1
		return self.tokens[self.i]
	
	def match(self, types : list[str]) :
		return self.current().type in types
	
	def consume_or_raise(self, types : list[str], message: str) :
		if self.match(types) :
			return self.current_and_advance()
		self.error_handler.error(ori='parser', token=self.current(), message=message)
		
	def expression(self) -> Expr.Expr:
		"""expression     → assignment ;"""
		return self.assignment()
	
	def assignment(self) -> Expr.Expr :
		"""
		assignment     → ( call "." )? IDENTIFIER "=" assignment | logic_or   ;
		"""
		expr = self.logic_or()
		if self.match(['EQUAL']) :
			equals = self.current_and_advance()
			value = self.assignment()
			if type(expr) == type(Expr.Variable(None)) :
				return Expr.Assign(expr.token, value)
			if isinstance(expr, Expr.Get) :
				return Expr.Set(expr.object, expr.token, value)
			
			self.error_handler.error(equals, "Invalid assignment target."); 
			
		return expr
	def logic_or(self) -> Expr.Expr :
		"""
		logic_or       → logic_and ( "or" logic_and )* ;
		"""
		left = self.logic_and()
		while self.match(['OR']) :
			operator = self.current_and_advance()
			right = self.term()
			left = Expr.Logical(left, operator, right)
		return left 
	
	def logic_and(self) -> Expr.Expr :
		"""
		logic_and      → equality ( "and" equality )* ;
		"""
		left = self.equality()
		while self.match(['AND']) :
			operator = self.current_and_advance()
			right = self.term()
			left = Expr.Logical(left, operator, right)
			
		return left

	
	def equality(self) -> Expr.Expr:
		"""equality       → comparison ( ( "!=" | "==" ) comparison )* ;"""
		left = self.comparison()
		while self.match(types=['BANG_EQUAL', "EQUAL_EQUAL"]) : 
			operator = self.current_and_advance()
			right = self.equality()
			left = Expr.Binary(left, operator, right)
		return left
	
	def comparison(self) -> Expr.Expr:
		"""comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;"""
		left = self.term()
		while self.match(types=['GREATER', 'GREATER_EQUAL', 'LESS', 'LESS_EQUAL']) :
			operator = self.current_and_advance()
			right = self.term()
			left = Expr.Binary(left, operator, right)
		return left
		
	def term(self) -> Expr.Expr:
		"""term           → factor ( ( "-" | "+" ) factor )* ;"""
		left = self.factor()
		while self.match(types=['MINUS', 'PLUS']) :
			operator = self.current_and_advance()
			right = self.factor()
			left = Expr.Binary(left, operator, right)
		return left
	
	def factor(self) -> Expr.Expr :
		"""factor         → unary ( ( "/" | "*" ) unary )* ;"""
		left = self.unary()
		while self.match(types=['SLASH', 'STAR']) :
			operator = self.current_and_advance()
			right = self.unary()
			left = Expr.Binary(left, operator, right)
		return left
	
	def unary(self) -> Expr.Expr :
		"""
			unary          → ( "!" | "-" ) unary
										| call  ;
		""" 
		if not self.match(types=['MINUS', 'BANG']) :
			return self.call() 
		operator = self.current_and_advance()
		right = self.unary()    
		return Expr.Unary(operator, right)
	
	def call(self) -> Expr.Expr :
		"""
		call           → primary ( "(" arguments? ")" | "." IDENTIFIER )* ;
		""" 
		expr = self.primary()
		while True:
			if self.match(types=['LEFT_PAREN']) :
				self.advance()
				expr = self.arguments(expr)
			elif self.match(types=['DOT']) :
				self.advance()
				token = self.consume_or_raise(['IDENTIFIER'], "expect property name after '.'")
				expr = Expr.Get(expr, token)
			else : 
				break
		return expr
	
	def arguments(self, callee: Expr.Expr) -> Expr.Expr :
		"""
		arguments      → expression ( "," expression )* ;
		""" 
		args: list[Expr.Expr] = []
		
		if not self.match(['RIGHT_PAREN']) :
			args.append(self.expression())
			while self.match(types=['COMMA']) :
				self.advance()
				args.append(self.expression()) 
		paren = self.consume_or_raise(['RIGHT_PAREN'], "Expect ')' after arguments")
		return Expr.Call(callee, paren, args)
	

	def primary(self) -> Expr.Expr :
		"""primary        → NUMBER | STRING | "true" | "false" | "None"
							 | "(" expression ")"   | "super" "." IDENTIFIER ;;
		"""
		if self.match(['NUMBER', 'STRING']) :
			return Expr.Literal(self.current_and_advance().literal)
		if self.match(['TRUE']) :
			self.advance()
			return Expr.Literal(True)
		if self.match(['FALSE']) :
			self.advance()
			return Expr.Literal(False)
		if self.match(['None']) :
			self.advance()
			return Expr.Literal(None)
		if self.match(['THIS']) :
			return Expr.This(self.current_and_advance())
		if self.match(['IDENTIFIER']) :
			return Expr.Variable(self.current_and_advance())
		if self.match(['LEFT_PAREN']) :
			self.advance()
			expr = self.expression()
			self.consume_or_raise(types=['RIGHT_PAREN'], message= "Expect ')' after expression.")
			return Expr.Grouping(expr)
		if self.match(['SUPER']) :
			keyword = self.current_and_advance()
			self.consume_or_raise(types=['DOT'], message= "Expect '.' after super.")
			method = self.consume_or_raise(types=['IDENTIFIER'], message= "Expect '.' after super.")
			return Expr.Super(keyword, method)
		self.error_handler.error(self.peek(), "Expect expression.")
		
	def synchronize(self) :
		""" In case of a parsing error :  try to find the next anchor to parse valid code """
		
		self.advance()

		while not self.isAtEnd() :
			if self.current().type == 'SEMICOLON' :
				return

			if self.peek().type \
			in ('CLASS', 'FUN', 'VAR', 'FOR', 'IF', 'WHILE', 'PRINT', 'RETURN') :
					return

			self.advance()
		
		

