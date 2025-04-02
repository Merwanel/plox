#  pytest  -vv
from __future__ import annotations

from Plox.ErrorHandling import ErrorHandling
from Plox.Scanner import Scanner
from Plox.Parser import Parser
from Plox.AstPrinter import AstPrinter
import Plox.Expr as Expr
import Plox.Stmt as Stmt
from Plox.Token import Token


def scan_and_parse(content: str)  -> str:
    error_handler = ErrorHandling()
    scanner = Scanner(error_handler)
    parser = Parser(error_handler, scanner)
    for i, line in enumerate(content.split('\n')) :
        scanner.scan(i, line)
   
    parser.parse()
    print(parser.statements)
    if len(parser.statements) >= 1 :
        klass = parser.statements[0]
        if isinstance(klass, Stmt.Class) :
            print('1',klass)
            print('2',klass.methods)
            meth = klass.methods[0] if len(klass.methods) >= 1 else None
            if isinstance(meth, Stmt.Function) :
                print('3', meth.body)
                p = meth.body[0] if len(meth.body) >= 1 else None
                if isinstance(p, Stmt.Print) :
                    print('4', p.expression)
    return error_handler.parser_errors +  AstPrinter().stringfyTree(parser.statements)


def test_1() :
    ast_str = scan_and_parse(content="""
        var a = 9 ;
    """)
    EXPECTED = AstPrinter().stringfyTree([
        Stmt.Var(
            token=Token(type = 'IDENTIFIER', lexeme='a', literal=None),
            initializer=Expr.Literal(float(9))
        )
    ])
    assert ast_str == EXPECTED
    
def test_2() :
    ast_str = scan_and_parse(content="""
        for(var i = 0 ; i < 10 ; i = i + 1) print i;
    """)
    token_i = Token('IDENTIFIER', 'i', None)
    var_i = Expr.Variable(token_i)
    token_less = Token('LESS', '<', None)
    token_plus = Token('PLUS', '+', None)
    EXPECTED = AstPrinter().stringfyTree([
        Stmt.Block([
            Stmt.Var(token_i, initializer=Expr.Literal(float(0)))
            ,Stmt.While(
                condition= Expr.Binary(var_i, token_less, Expr.Literal(10.0))
                ,body=Stmt.Block([
                    Stmt.Print(var_i)
                    ,Stmt.Expression(Expr.Assign(token_i, Expr.Binary(var_i, token_plus, Expr.Literal(1.0)) ))
                ])
            )
        ])
    ])
    assert ast_str == EXPECTED
      
def test_3() :
    ast_str = scan_and_parse(content="""
        fun sayHi(first, last) {
            print "Hi, " + first + " " + last + "!";
        }

        sayHi("Dear", "Reader");
    """)
    token_plus = Token('PLUS', '+', None)
    token_first = Token('IDENTIFIER','first', None)
    token_last = Token('IDENTIFIER','last', None)
    var_first = Expr.Variable(token_first)
    var_last = Expr.Variable(token_last)
    EXPECTED = AstPrinter().stringfyTree([
        Stmt.Function(
            token=Token('IDENTIFIER', 'sayHi', None)
            ,params=[
                token_first
                ,token_last
            ]
            ,body=[
                Stmt.Print(
                    Expr.Binary(
                        Expr.Binary(
                            Expr.Binary(
                                Expr.Binary( Expr.Literal('Hi, '), token_plus, var_first)
                                , token_plus, Expr.Literal(" "))
                            , token_plus, var_last)
                        , token_plus, Expr.Literal("!"))
                )
            ]
        )
        ,Stmt.Expression(
            Expr.Call(
                Expr.Variable(Token('IDENTIFIER', 'sayHi', None))
                ,Token('LEFT_PAREN', '(', None)
                ,[Expr.Literal('Dear'), Expr.Literal('Reader')]
            )
        )
    ])
    assert ast_str == EXPECTED
    
def test_class_instance_print() :
    ast_str = scan_and_parse(content="""
        class Bagel {}
        var bagel = Bagel();
        print bagel; // Prints "Bagel instance".
    """)
    token_Bagel = Token('IDENTIFIER', 'Bagel', 'None')
    var_Bagel = Expr.Variable(token_Bagel)
    token_bagel = Token('IDENTIFIER', 'bagel', 'None')
    var_bagel = Expr.Variable(token_bagel)
    EXPECTED = AstPrinter().stringfyTree([
        Stmt.Class(
            token_Bagel
            , methods=[]
        )
        ,Stmt.Var(
            token_bagel
            ,initializer=Expr.Call(var_Bagel, paren=Token('LEFT_PAREN', '(', None),arguments=[])
        )
        ,Stmt.Print(var_bagel)
    ])
    assert ast_str == EXPECTED
    
    
def test_class_method() :
    ast_str = scan_and_parse(content="""
        class Bacon {
            eat() {
                print "Crunch crunch crunch!";
            }
        }

        Bacon().eat(); // Prints "Crunch crunch crunch!".
    """)
    EXPECTED = AstPrinter().stringfyTree([
        Stmt.Class(
            Token('IDENTIFIER', 'Bacon', None)
            , methods=[
                Stmt.Function(
                    Token('IDENTIFIER', 'eat', None)
                    ,params=[]
                    ,body=[Stmt.Print(Expr.Literal("Crunch crunch crunch!"))]
                )
            ]
        )
        , Stmt.Expression(
            Expr.Call(
                callee=Expr.Get(
                    object=Expr.Call(
                        callee=Expr.Variable(Token('IDENTIFIER', 'Bacon', None))
                        ,paren=Token('LEFT_PAREN', '(', None)
                        ,arguments=[]
                    )
                    ,token=Token('IDENTIFIER', 'eat', None)   
                )
                ,paren=Token('LEFT_PAREN', '(', None)
                ,arguments=[]
            )
        )
    ])
    assert ast_str == EXPECTED
    
def test_scope_closure() :
    ast_str = scan_and_parse(content="""
        var a = "global";
        {
            fun showA() {
                print a;
            }

                showA();
                var a = "block";
                showA();
        }
    """)
    token_a = Token(type = 'IDENTIFIER', lexeme='a', literal=None)
    token_showA = Token('IDENTIFIER', 'showA', 'None')
    var_showA = Expr.Variable(token_showA)
     
    EXPECTED =  AstPrinter().stringfyTree([
        Stmt.Var(
            token=token_a,
            initializer=Expr.Literal('global')
        ),
        Stmt.Block([
            Stmt.Function(
                token=token_showA,
                params=[],
                body=[Stmt.Print(Expr.Variable(token_a))]
            ),
            Stmt.Expression(Expr.Call(callee=var_showA, paren=Token('LEFT_PAREN', '(', None),arguments=[])),
            Stmt.Var(
                token=token_a,
                initializer=Expr.Literal('block')
            ),
            Stmt.Expression(Expr.Call(callee=var_showA, paren=Token('LEFT_PAREN', '(', None),arguments=[]))
        ])
    ])
    assert ast_str == EXPECTED