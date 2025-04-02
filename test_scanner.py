#  pytest  -vv
import os
from Plox.Scanner import Scanner

from Plox.ErrorHandling import ErrorHandling


def tokenize(content: str)  -> list[str]:
    error_handler = ErrorHandling()
    scanner = Scanner(error_handler)
    for i, line in enumerate(content.split('\n')) :
        scanner.scan(i, line)
    print('tok:',[f"{s}" for s in error_handler.lexical_errors + scanner.tokens])
    return  error_handler.lexical_errors + [ str(token) for token in scanner.tokens]
     
def test_1() :
    tokens = tokenize(content='(())')
    EXPECTED = ['LEFT_PAREN ( None', 'LEFT_PAREN ( None', 'RIGHT_PAREN ) None', 'RIGHT_PAREN ) None', 'EOF  None']
    assert tokens == EXPECTED
def test_2() :
    tokens = tokenize(content='{(}()#')
    EXPECTED = ['[line 1] Error: Unexpected character: #', 'LEFT_BRACE { None', 'LEFT_PAREN ( None', 'RIGHT_BRACE } None', 'LEFT_PAREN ( None', 'RIGHT_PAREN ) None','EOF  None']
    assert tokens == EXPECTED
def test_3() :
    tokens = tokenize(content=',.$(#')
    EXPECTED = ['[line 1] Error: Unexpected character: $','[line 1] Error: Unexpected character: #', 'COMMA , None', 'DOT . None', 'LEFT_PAREN ( None',  'EOF  None']
    assert tokens == EXPECTED
def test_4() :
    tokens = tokenize(content='={===}')
    EXPECTED = ['EQUAL = None','LEFT_BRACE { None','EQUAL_EQUAL == None', 'EQUAL = None', 'RIGHT_BRACE } None', 'EOF  None']
    assert tokens == EXPECTED
def test_5() :
    tokens = tokenize(content='((==@====%))')
    EXPECTED = ['[line 1] Error: Unexpected character: @','[line 1] Error: Unexpected character: %'
                , 'LEFT_PAREN ( None', 'LEFT_PAREN ( None','EQUAL_EQUAL == None','EQUAL_EQUAL == None'
                ,'EQUAL_EQUAL == None', 'RIGHT_PAREN ) None', 'RIGHT_PAREN ) None','EOF  None']
    assert tokens == EXPECTED
def test_6() :
    tokens = tokenize(content='!!===')
    EXPECTED = ['BANG ! None','BANG_EQUAL != None','EQUAL_EQUAL == None','EOF  None']
    assert tokens == EXPECTED
def test_7() :
    tokens = tokenize(content='/')
    EXPECTED = ['SLASH / None','EOF  None']
    assert tokens == EXPECTED
def test_8() :
    tokens = tokenize(content='// comment')
    EXPECTED = ['EOF  None']
    assert tokens == EXPECTED
def test_9() :
    tokens = tokenize(content='( )\n\t')
    EXPECTED = ['LEFT_PAREN ( None','RIGHT_PAREN ) None', 'EOF  None']
    assert tokens == EXPECTED
def test_10() :
    tokens = tokenize(content='"foo baz"')
    EXPECTED = ['STRING "foo baz" foo baz','EOF  None']
    assert tokens == EXPECTED
def test_11() :
    tokens = tokenize(content='"hello"')
    EXPECTED = ['STRING "hello" hello','EOF  None']
    assert tokens == EXPECTED
def test_12() :
    tokens = tokenize(content='"bar')
    EXPECTED = ['[line 1] Error: Unterminated string.','EOF  None']
    assert tokens == EXPECTED
def test_13() :
    tokens = tokenize(content='"foo <\t>bar 123 // hello world!"')
    EXPECTED = ['STRING "foo <\t>bar 123 // hello world!" foo <\t>bar 123 // hello world!','EOF  None']
    assert tokens == EXPECTED
def test_14() :
    tokens = tokenize(content='1234.1234')
    EXPECTED = ['NUMBER 1234.1234 1234.1234','EOF  None']
    assert tokens == EXPECTED
def test_15() :
    tokens = tokenize(content='1234.1234.1234.')
    EXPECTED = ['NUMBER 1234.1234 1234.1234', "DOT . None",'NUMBER 1234 1234.0', "DOT . None",'EOF  None']
    assert tokens == EXPECTED
def test_16() :
    tokens = tokenize(content='"Hello" = "Hello" && 42 == 42')
    EXPECTED = ['[line 1] Error: Unexpected character: &','[line 1] Error: Unexpected character: &'
                ,'STRING "Hello" Hello','EQUAL = None','STRING "Hello" Hello','NUMBER 42 42.0', 'EQUAL_EQUAL == None', 'NUMBER 42 42.0','EOF  None']
    assert tokens == EXPECTED
def test_17() :
    tokens = tokenize(content='foo bar _hello')
    EXPECTED = ['IDENTIFIER foo None','IDENTIFIER bar None','IDENTIFIER _hello None','EOF  None']
    assert tokens == EXPECTED
def test_18() :
    tokens = tokenize(content='num2 = 200.00')
    EXPECTED = ['IDENTIFIER num2 None', 'EQUAL = None','NUMBER 200.00 200.0','EOF  None']
    assert tokens == EXPECTED
def test_19() :
    tokens = tokenize(content='and')
    EXPECTED = ['AND and None','EOF  None']
    assert tokens == EXPECTED
def test_addition() :
    tokens = tokenize(content="""
        var a = 5 ;
        var b = 6 ;
        var c = a + b ;
        print a ;
    """)
    EXPECTED = ['VAR var None','IDENTIFIER a None','EQUAL = None','NUMBER 5 5.0','SEMICOLON ; None','VAR var None','IDENTIFIER b None',
                'EQUAL = None','NUMBER 6 6.0','SEMICOLON ; None','VAR var None','IDENTIFIER c None','EQUAL = None','IDENTIFIER a None',
                'PLUS + None','IDENTIFIER b None','SEMICOLON ; None','PRINT print None','IDENTIFIER a None','SEMICOLON ; None','EOF  None',]
    assert tokens == EXPECTED

def test_20() :
    tokens = tokenize(content="""var a = 9 ;
        fun sayHi(first, last) {
            print "Hi, " + first + " " + last + "!";
            print 5 + 8 + a ;
        }

        sayHi("Dear", "Reader");
        """)
            
    EXPECTED = ['VAR var None', 'IDENTIFIER a None', 'EQUAL = None', 'NUMBER 9 9.0', 'SEMICOLON ; None', 'FUN fun None'
                , 'IDENTIFIER sayHi None', 'LEFT_PAREN ( None', 'IDENTIFIER first None', 'COMMA , None', 'IDENTIFIER last None'
                , 'RIGHT_PAREN ) None', 'LEFT_BRACE { None', 'PRINT print None', 'STRING "Hi, " Hi, ', 'PLUS + None'
                , 'IDENTIFIER first None', 'PLUS + None', 'STRING " "  ', 'PLUS + None', 'IDENTIFIER last None'
                , 'PLUS + None', 'STRING "!" !', 'SEMICOLON ; None', 'PRINT print None', 'NUMBER 5 5.0', 'PLUS + None'
                , 'NUMBER 8 8.0', 'PLUS + None', 'IDENTIFIER a None', 'SEMICOLON ; None', 'RIGHT_BRACE } None', 'IDENTIFIER sayHi None'
                , 'LEFT_PAREN ( None', 'STRING "Dear" Dear', 'COMMA , None', 'STRING "Reader" Reader', 'RIGHT_PAREN ) None'
                , 'SEMICOLON ; None', 'EOF  None']
    assert tokens == EXPECTED
def test_21() :
    tokens = tokenize(content="""var a = "global a";
                                var b = "global b";
                                var c = "global c";
                                {
                                var a = "outer a";
                                var b = "outer b";
                                {
                                    var a = "inner a";
                                    print a;
                                    print b;
                                    print c;
                                }
                                print a;
                                print b;
                                print c;
                                }
                                print a;
                                print b;
                                print c;
    """)
    EXPECTED = ['VAR var None', 'IDENTIFIER a None', 'EQUAL = None', 'STRING "global a" global a', 'SEMICOLON ; None'
                , 'VAR var None', 'IDENTIFIER b None', 'EQUAL = None', 'STRING "global b" global b', 'SEMICOLON ; None'
                , 'VAR var None', 'IDENTIFIER c None', 'EQUAL = None', 'STRING "global c" global c', 'SEMICOLON ; None'
                , 'LEFT_BRACE { None', 'VAR var None', 'IDENTIFIER a None', 'EQUAL = None', 'STRING "outer a" outer a'
                , 'SEMICOLON ; None', 'VAR var None', 'IDENTIFIER b None', 'EQUAL = None', 'STRING "outer b" outer b'
                , 'SEMICOLON ; None', 'LEFT_BRACE { None', 'VAR var None', 'IDENTIFIER a None', 'EQUAL = None'
                , 'STRING "inner a" inner a', 'SEMICOLON ; None', 'PRINT print None', 'IDENTIFIER a None'
                , 'SEMICOLON ; None', 'PRINT print None', 'IDENTIFIER b None', 'SEMICOLON ; None', 'PRINT print None'
                , 'IDENTIFIER c None', 'SEMICOLON ; None', 'RIGHT_BRACE } None', 'PRINT print None', 'IDENTIFIER a None'
                , 'SEMICOLON ; None', 'PRINT print None', 'IDENTIFIER b None', 'SEMICOLON ; None', 'PRINT print None'
                , 'IDENTIFIER c None', 'SEMICOLON ; None', 'RIGHT_BRACE } None', 'PRINT print None', 'IDENTIFIER a None'
                , 'SEMICOLON ; None', 'PRINT print None', 'IDENTIFIER b None', 'SEMICOLON ; None', 'PRINT print None'
                , 'IDENTIFIER c None', 'SEMICOLON ; None', 'EOF  None']
    assert tokens == EXPECTED
    
def test_22() :
    tokens = tokenize(content="""
    class Bacon {
        eat() {
            print "Crunch crunch crunch!";
        }
    }

    Bacon().eat(); // Prints "Crunch crunch crunch!".
    """)
    EXPECTED = [
        'CLASS class None','IDENTIFIER Bacon None','LEFT_BRACE { None'
        ,'IDENTIFIER eat None', 'LEFT_PAREN ( None','RIGHT_PAREN ) None','LEFT_BRACE { None'
        ,'PRINT print None','STRING "Crunch crunch crunch!" Crunch crunch crunch!','SEMICOLON ; None'
        ,'RIGHT_BRACE } None','RIGHT_BRACE } None','IDENTIFIER Bacon None','LEFT_PAREN ( None'
        ,'RIGHT_PAREN ) None','DOT . None','IDENTIFIER eat None','LEFT_PAREN ( None'
        , 'RIGHT_PAREN ) None','SEMICOLON ; None','EOF  None'
    ]
    assert tokens == EXPECTED
def test_scope_closure() :
    tokens = tokenize(content="""
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
    EXPECTED = ['VAR var None','IDENTIFIER a None','EQUAL = None','STRING "global" global','SEMICOLON ; None',
                'LEFT_BRACE { None','FUN fun None','IDENTIFIER showA None','LEFT_PAREN ( None','RIGHT_PAREN ) None',
                'LEFT_BRACE { None','PRINT print None','IDENTIFIER a None','SEMICOLON ; None','RIGHT_BRACE } None',
                'IDENTIFIER showA None','LEFT_PAREN ( None','RIGHT_PAREN ) None','SEMICOLON ; None','VAR var None',
                'IDENTIFIER a None','EQUAL = None','STRING "block" block','SEMICOLON ; None','IDENTIFIER showA None',
                'LEFT_PAREN ( None','RIGHT_PAREN ) None','SEMICOLON ; None','RIGHT_BRACE } None','EOF  None',]
    assert tokens == EXPECTED