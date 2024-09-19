import time
from Expr import Expr
from Stmt import Stmt 
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
        self.locals = dict()
        self.environment.values["clock"] = ClockFn()

    
    def interpret(self):
        try:
            for statement in self.statements:
                statement.execute(self)
        except Exception as e:
            print("Runtime error", {e})
            exit(1)
    

    def resolve(self, expr: Expr, depth: int):
        self.locals[expr] = depth
    

    def lookUpVar(self, name: str, expr: Expr):
        dist = self.locals[expr]
        return self.environment.getAt(dist, name)