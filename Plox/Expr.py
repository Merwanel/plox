from __future__ import annotations
from Plox.Token import Token
from abc import ABC, abstractmethod


class Expr(ABC) :
  """unit that will represent a value after evaluation"""
  @abstractmethod
  def accept(self, visitor: Visitor)  :
     pass
     
class Assign(Expr) :
  def __init__(self, token: Token, expr: Expr) -> None:
    self.token = token
    self.expr = expr
  def accept(self, visitor: Visitor) :
    return visitor.visitAssignExpr(self)
  
class Binary(Expr) :
  def __init__(self, left :Expr, operator: Token, right :Expr) -> None:
    self.left = left
    self.operator = operator
    self.right = right
  def accept(self, visitor: Visitor) :
    return visitor.visitBinary(self)

class Call(Expr) :
  def __init__(self, callee: Expr, paren : Token, arguments: list[Expr]) :
    self.callee = callee
    self.paren = paren
    self.arguments = arguments
  def accept(self, visitor: Visitor) :
    return visitor.visitCall(self)
    
class Literal(Expr) :
  def __init__(self, value) -> None:
        self.value = value
  def accept(self, visitor: Visitor) :
    return visitor.visitLiteral(self)

class Logical(Expr) :
  def __init__(self, left :Expr, operator: Token, right :Expr) -> None:
    self.left = left
    self.operator = operator
    self.right = right
  def accept(self, visitor: Visitor) :
    return visitor.visitLogicalExpr(self)

class Set(Expr) :
  def __init__(self, object: Expr, token: Token, value: Expr) -> None:
    self.object = object
    self.token = token
    self.value = value
  def accept(self, visitor: Visitor) :
    return visitor.visitSet(self)

class Super(Expr) :
  def __init__(self, keyword: Token, method: Token) -> None:
    self.keyword = keyword
    self.method = method
  def accept(self, visitor: Visitor) :
    return visitor.visitSuper(self)

class This(Expr) :
  def __init__(self, keyword : Token) -> None:
    self.keyword = keyword
  def accept(self, visitor: Visitor) :
    return visitor.visitThis(self)

class Unary(Expr) :
  def __init__(self, operator: Token, right :Expr) -> None:
        self.operator = operator
        self.right = right
  def accept(self, visitor: Visitor) :
    return visitor.visitUnary(self)

class Get(Expr) :
  def __init__(self, object: Expr, token : Token) -> None :
    self.object = object
    self.token = token
  def accept(self, visitor: Visitor) :
    return visitor.visitGet(self)  

class Grouping(Expr) :
  def __init__(self, expression : Expr) -> None:
        self.expression = expression
  def accept(self, visitor: Visitor) :
    return visitor.visitGrouping(self)

class Variable(Expr) :
  def __init__(self, token : Token) -> None:
        self.token = token
  def accept(self, visitor: Visitor) :
    return visitor.visitVariableExpr(self)



class Visitor(ABC) :
  @abstractmethod
  def visitAssignExpr(self, expr : Assign) :
    pass
  @abstractmethod
  def visitBinary(self, expr : Binary) :
    pass
  @abstractmethod
  def visitCall(self, expr: Call) :
    pass
  @abstractmethod
  def visitLiteral(self, expr : Literal) :
    pass
  @abstractmethod
  def visitLogicalExpr(self, expr : Logical) :
    pass
  @abstractmethod
  def visitSet(self, expr : Set) :
    pass
  @abstractmethod
  def visitSuper(self, expr : Super) :
    pass
  @abstractmethod
  def visitThis(self, expr : This) :
    pass
  @abstractmethod
  def visitUnary(self, expr : Unary) :
    pass
  @abstractmethod
  def visitGet(self, expr : Get) :
    pass
  @abstractmethod
  def visitGrouping(self, expr : Grouping) :
    pass
  @abstractmethod
  def visitVariableExpr(self, expr : Variable) :
    pass