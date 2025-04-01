#  pytest  -vv
from __future__ import annotations
import Plox.Plox as Plox
from Plox.Natives import LoxArray

def scan_and_parse_and_interpret(content: str)  -> str:
    interpreter = Plox.Plox(is_a_test=True)
    for i, line in enumerate(content.split('\n')) :
        interpreter.scanner.scan(i, line)
   
    interpreter.parser.parse()
    interpreter.astResolver.resolve(interpreter.parser.statements)
    interpreter.astInterpreter.interpret(interpreter.parser.statements)
    return interpreter.error_handler.astInterpreter_errors +  interpreter.astInterpreter.printed


def test_print() :
    ast_str = scan_and_parse_and_interpret(content="""
        var a = 9 ; print a;
    """)
    EXPECTED = [9.0]
    assert ast_str == EXPECTED

def test_scope() :
    ast_str = scan_and_parse_and_interpret(content="""
        var a = "global a";
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
    EXPECTED = ['inner a','outer b','global c','outer a','outer b','global c','global a','global b','global c',]
    assert ast_str == EXPECTED
    
def test_loop() :
    ast_str = scan_and_parse_and_interpret(content="""
        for(var i = 0 ; i < 10 ; i = i + 1) print i;
    """)
    EXPECTED = [0.,1.,2.,3.,4.,5.,6.,7.,8.,9.]
    assert ast_str == EXPECTED
    
    
def test_fun_1() :
    ast_str = scan_and_parse_and_interpret(content="""
        fun sayHi(first, last) {
            print "Hi, " + first + " " + last + "!";
        }

        sayHi("Dear", "Reader");
    """)
    EXPECTED = ["Hi, Dear Reader!"]
    assert ast_str == EXPECTED
    
def test_fun_2() :
    ast_str = scan_and_parse_and_interpret(content="""
        var a = 45;
        fun my_fun() {
            print a;
        }
        my_fun()
    """)
    EXPECTED = [45.]
    assert ast_str == EXPECTED
    
def test_fun_3() :
    ast_str = scan_and_parse_and_interpret(content="""
        var a = 45;
        fun my_fun() {
            print a;
        }
        a = 77;
        my_fun()
    """)
    EXPECTED = [77.]
    assert ast_str == EXPECTED
    
def test_recursion() :
    ast_str = scan_and_parse_and_interpret(content="""
        fun fib(n) {
            if (n <= 1) return n;
            return fib(n - 2) + fib(n - 1);
        }

        for (var i = 0; i < 15; i = i + 1) {
            print fib(i);
        }
    """)
    EXPECTED = [0., 1., 1., 2., 3., 5., 8., 13., 21., 34., 55., 89., 144.0, 233.0,377.0,]
    assert ast_str == EXPECTED
    
def test_closure() :
    ast_str = scan_and_parse_and_interpret(content="""
        fun makeCounter() {
            var i = 0;
            fun count() {
                i = i + 1;
                print i;
            }

            return count;
        }

        var counter = makeCounter();
        counter(); // "1".
        counter(); // "2".
    """)
    EXPECTED = [1.,2.]
    assert ast_str == EXPECTED
    
def test_closure_and_scope() :
    ast_str = scan_and_parse_and_interpret(content="""
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
    EXPECTED = ["global", "global"]
    assert ast_str == EXPECTED
 
def test_class_print() :
    ast_str = scan_and_parse_and_interpret(content="""
        class DevonshireCream {
            serveOn() {
                return "Scones";
            }
        }

        print DevonshireCream; // Prints "DevonshireCream".
    """)
    EXPECTED = ['DevonshireCream']
    assert [str(s) for s in ast_str] == EXPECTED
    
  
def test_class_instance_print() :
    ast_str = scan_and_parse_and_interpret(content="""
        class Bagel {}
        var bagel = Bagel();
        print bagel; // Prints "Bagel instance".
    """)
    EXPECTED = ['Bagel instance']
    assert [str(s) for s in ast_str] == EXPECTED

def test_class() :
    ast_str = scan_and_parse_and_interpret(content="""   
    class Bacon {
        eat() {
            print "Crunch crunch crunch!";
        }
    }

    Bacon().eat(); // Prints "Crunch crunch crunch!".
    """)
    EXPECTED = ['Crunch crunch crunch!']
    assert ast_str  == EXPECTED


def test_class2() :
    ast_str = scan_and_parse_and_interpret(content="""   
        class Person {
            sayName() {
                print this.name;
            }
        }

        var jane = Person();
        jane.name = "Jane";

        var method = jane.sayName;
        method(); // ?
    """)
    EXPECTED = ["""Jane"""]
    assert ast_str  == EXPECTED
    
def test_class_weird() :
    ast_str = scan_and_parse_and_interpret(content="""   
        class Person {
            sayName() {
                print this.name;
            }
        }

        var jane = Person();
        jane.name = "Jane";

        var bill = Person();
        bill.name = "Bill";

        bill.sayName = jane.sayName;
        bill.sayName(); // ?
    """)
    EXPECTED = ["""Jane"""]
    assert ast_str  == EXPECTED
    
    
def test_class_weird2() :
    ast_str = scan_and_parse_and_interpret(content="""               
        class Box {}

        fun notMethod(argument) {
        print "called function with " + argument;
        }

        var box = Box();
        box.function = notMethod;
        box.function("argument");
    """)
    EXPECTED = ["""called function with argument"""]
    assert ast_str  == EXPECTED
    

def test_class_this() :
    ast_str = scan_and_parse_and_interpret(content="""   
    class Cake {
        taste() {
            var adjective = "delicious";
            print "The " + this.flavor + " cake is " + adjective + "!";
        }
    }

    var cake = Cake();
    cake.flavor = "German chocolate";
    cake.taste(); // Prints "The German chocolate cake is delicious!".
    """)
    EXPECTED = ['The German chocolate cake is delicious!']
    assert ast_str  == EXPECTED

def test_class_constructor() :
    ast_str = scan_and_parse_and_interpret(content="""   
    class Square {
        init() {
            this.L = 5;
        }
    }
    print Square().L
    """)
    EXPECTED = [5.0]
    assert ast_str  == EXPECTED
 
def test_class_inheritance() :
    ast_str = scan_and_parse_and_interpret(content="""   
        class Doughnut {
            cook() {
                print "Fry until golden brown.";
            }
        }

        class BostonCream < Doughnut {}

        BostonCream().cook();
    """)
    EXPECTED = ["""Fry until golden brown."""]
    assert ast_str  == EXPECTED


def test_error_class_inheritance2() :
    ast_str = scan_and_parse_and_interpret(content="""   
        var NotAClass = "I am totally not a class";
        class Subclass < NotAClass {} // ?!
    """)
    EXPECTED = ["""SuperClass must be a class"""]
    assert [str(s) for s in ast_str]  == EXPECTED

def test_class_inheritance_super() :
    ast_str = scan_and_parse_and_interpret(content="""   
        class Doughnut {
            cook() {
                print "Fry until golden brown.";
            }
        }

        class BostonCream < Doughnut {
            cook() {
                super.cook();
                print "Pipe full of custard and coat with chocolate.";
            }
        }

        BostonCream().cook();
    """)
    EXPECTED = ["""Fry until golden brown.""", """Pipe full of custard and coat with chocolate."""]
    assert ast_str == EXPECTED

def test_class_inheritance_super2() :
    ast_str = scan_and_parse_and_interpret(content="""   
        class A {
            method() {
                print "A method";
            }     
        }

        class B < A {
            method() {
                print "B method";
            }

            test() {
                super.method();
            }
        }

        class C < B {}

        C().test();
    """)
    EXPECTED = ["""A method"""]
    assert ast_str == EXPECTED

def test_Native_Array1() :
    ast_str = scan_and_parse_and_interpret(content="""           
        var array = Array(3);
        print array; 
    """)
    EXPECTED =[LoxArray(3)]
    assert ast_str == EXPECTED

def test_Native_Array2() :
    ast_str = scan_and_parse_and_interpret(content="""           
    
        var array = Array(3);

        // "length" returns the number of elements.
        print array.length; // "3".

        // "set" sets the element at the given index to the given value.
        array.set(1, "new");

        // "get" returns the element at a given index.
        print array.get(1); // "new".
    """)
    EXPECTED =[3., 'new']
    assert ast_str == EXPECTED


def test_Native_Array1() :
    ast_str = scan_and_parse_and_interpret(content="""   
        fun fib(n) {
            if (n < 2) return n;
            return fib(n - 1) + fib(n - 2); 
        }        
        var before = clock();
        print fib(4);
        var after = clock();
        print after - before;
    """)
    assert len(ast_str) == 2 
    assert type(ast_str[1]) == float
    assert ast_str[1] < 1 
