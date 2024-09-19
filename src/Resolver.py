from enum import Enum
from Expr import Expr

class Resolver:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = []
        self.scopes.append(dict())
        self.currentFunction = 'None' 
    

    def resolve(self) -> None:
        for statement in self.interpreter.statements:
            statement.resolve(self)
    

    def beginScope(self) -> None:
        self.scopes.append(dict())
    

    def endScope(self) -> None:
        self.scopes.pop()
    

    def declare(self, name: str) -> None:
        if not self.scopes:
            return
        
        scope = self.scopes[-1]
        if name in scope:
            print("Already a variable with same name in this scope.")
            exit(1)
        scope[name] = False
    

    def define(self, name: str) -> None:
        if not self.scopes:
            return
        
        self.scopes[-1][name] = True
    

    def resolveLocal(self, expr: Expr, name: str) -> None:
        for i in range(len(self.scopes) - 1, -1, -1):
            if name in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - i - 1)
                return