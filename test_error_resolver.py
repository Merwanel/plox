#  pytest  -vv
from __future__ import annotations
import Plox.Plox as Plox
import Plox.Token as Token


def scan_and_parse_and_interpret(content: str)  -> str:
    interpreter = Plox.Plox(is_a_test=True)
    for i, line in enumerate(content.split('\n')) :
        interpreter.scanner.scan(i, line)
   
    interpreter.parser.parse()
    interpreter.astResolver.resolve(interpreter.parser.statements)
    return interpreter.error_handler.resolver_errors +  interpreter.astInterpreter.printed

 
def test_error_scope() :
    ast_str = scan_and_parse_and_interpret(content="""
        var a = "outer";
        {
            var a = a;
        }
    """)
    EXPECTED = ["a Can't read local variable in its own initializer."]
    assert ast_str == EXPECTED
    
def test_error_return_at_top_level() :
    ast_str = scan_and_parse_and_interpret(content="""
        return "at top level";
    """)
    EXPECTED = [f"""{Token.Token("STRING", "at top level", "at top level")}, Can't return from top-level code."""]
    assert ast_str == EXPECTED

def test_error_class_init() :
    ast_str = scan_and_parse_and_interpret(content="""   
        class Foo {
            init() {
                return "something else";
            }
        }
    """)
    EXPECTED = [f"""{Token.Token("STRING", "something else", "something else")}, Can\'t return from an initializer."""]
    assert ast_str  == EXPECTED

def test_error_class_inheritance() :
    ast_str = scan_and_parse_and_interpret(content="""   
        class Oops < Oops {}
    """)
    EXPECTED = ["""Oops, A class can't inherit from itself."""]
    assert ast_str  == EXPECTED
 
def test_error_class_super() :
    ast_str = scan_and_parse_and_interpret(content="""   
       class Eclair {
            cook() {
                super.cook();
                print "Pipe full of crème pâtissière.";
            }
        }
    """)
    EXPECTED = ["""super, Can't use 'super' in a class with no superclass."""]
    assert ast_str  == EXPECTED
    
def test_error_class_super2() :
    ast_str = scan_and_parse_and_interpret(content="""   
       super.notEvenAClass();
    """)
    EXPECTED = ["""super, Can't use 'super' outside of a class."""]
    assert ast_str  == EXPECTED
 