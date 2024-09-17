from enum import Enum

FunctionType = Enum('FunctionType', [
    'NONE',
    'FUNCTION',
    'METHOD'
])

class Resolver:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = []
        self.scopes.append(dict())
        self.currentFunction = FunctionType.NONE
    

    def resolve(self):
        for statement in self.interpreter.statements:
            statement.resolve(self)
    

    def beginScope(self):
        self.scopes.append(dict())
    

    def endScope(self):
        self.scopes.pop()
    

    def declare(self, name):
        if not self.scopes:
            return
        
        scope = self.scopes[-1]
        if name in scope:
            print("Already a variable with same name in this scope.")
            exit(1)
        scope[name] = False
    

    def define(self, name):
        if not self.scopes:
            return
        
        self.scopes[-1][name] = True
    

    def resolveLocal(self, expr, name):
        for i in range(len(self.scopes) - 1, -1, -1):
            if name in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - i - 1)
                return