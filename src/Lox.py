import sys
from Token import *
from Scanner import *
from Parser import *
from Interpreter import *
from Resolver import Resolver

class Lox:
    def run(self, source: str) -> None:
        scanner = Scanner(source)
        tokens = scanner.scan()
        # print("\nScanner")
        # for token in tokens:
        #     print(token)
        parser = Parser(tokens)
        statements = parser.parse()
        # print("\nParser")
        # for statement in statements:
        #     print(statement)
        # print("\nInterpreter")
        interpreter = Interpreter(statements)
        resolver = Resolver(interpreter)
        resolver.resolve()
        interpreter.interpret()


    def runFile(self, path: str) -> None:
        try:
            with open(path) as file:
                data = file.read()
                self.run(data)
        except FileNotFoundError:
            print(f"I/O error: File '{path}' does not exist")
            exit(1)
        except PermissionError:
            print(f"I/O error: Access denied")
            exit(1)
        except IOError as e:
            print(f"I/O error: {e}")
            exit(1)


    def runPromt(self) -> None:
        line = ""
        while True:
            try:
                line = input("> ")
            except EOFError:
                print()
                sys.exit(0)

            self.run(line)


def main():
    lox = Lox()
    argc = len(sys.argv)
    if argc < 2:
        lox.runPromt()
    elif argc == 2:
        lox.runFile(sys.argv[1])
    else:
        print("Wrong usage, correct usage: plox path/to/script")
        sys.exit(1)


if __name__ == '__main__':
    main()
