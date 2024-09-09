import time
from Stmt import *
from Environment import *
from LoxCallable import LoxCallable

class ClockFn(LoxCallable):
    def arity(self):
        return 0
    

    def call(self, environment, arguments):
        return time.time()
    

    def __str__(self):
        return "<native fn clock>"


class Interpreter:
    def __init__(self, statements: list[Stmt]):
        self.statements = statements
        self.environment = Environment() 
        self.environment.values["clock"] = ClockFn()

    
    def interpret(self):
        try:
            for statement in self.statements:
                statement.execute(self.environment)
        except Exception as e:
            print("Runtime error", {e})
            exit(1)