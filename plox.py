# python3 plox.py file_example.txt


from io import TextIOWrapper
import sys

from Plox.Plox import Plox
import Plox.Expr as Expr 

def run(interpreter:Plox, file :TextIOWrapper=None) :
    for i, line in enumerate(file) :
        interpreter.scanner.scan(i, line)
    interpreter.parser.parse()
    # print('-----------------')
    # print(AstPrinter().stringfyTree(interpreter.parser.statements))
    # print('-----------------')
    interpreter.astResolver.resolve(interpreter.parser.statements)
    interpreter.astInterpreter.interpret(interpreter.parser.statements)
    
def runPrompt(interpreter:Plox) :
  line = ''
  i = 0
  while True :
    i += 1
    line = input('>')
    interpreter.scanner.scan(i, line)
    syntax = interpreter.parser.parseRepl()

    if interpreter.error_handler.has_lexical_errors :
        continue
    
    if type(syntax) == list :
      interpreter.astInterpreter.interpret(syntax)
    elif (type(syntax) == type(Expr.Expr())) :
      result = interpreter.astInterpreter.interpret(syntax)
      if result != None :
        print("=", result)


def main():
    interpreter = Plox()

    if len(sys.argv) > 2:
        print("Usage: plox.py <filename>", file=sys.stderr)
        exit(1)

    if len(sys.argv) == 2:
        filename = sys.argv[1]
        with open(filename) as file:
            run(interpreter, file=file)
        if interpreter.error_handler.has_lexical_errors :
            exit(65)
    else :
        runPrompt(interpreter)

if __name__ == "__main__":
    main()