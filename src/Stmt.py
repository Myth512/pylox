from abc import ABC, abstractmethod
from Expr import *
from LoxFunction import LoxFunction 
from ReturnException import ReturnException
from Resolver import Resolver
from LoxClass import LoxClass

class Stmt:
    @abstractmethod
    def execute(self, interpreter):
        pass


    @abstractmethod
    def resolve(self, resolver):
        pass


class Expression(Stmt):
    def __init__(self, expression):
        self.expression: Expr = expression

    
    def execute(self, interpreter):
        return self.expression.evaluate(interpreter)


    def resolve(self, resolver):
        self.expression.resolve(resolver)


    def __str__(self):
        return f'expr {self.expression}'


class Print(Stmt):
    def __init__(self, expression):
        self.expression: Expr = expression

    
    def execute(self, interpreter):
        print(self.expression.evaluate(interpreter))
    

    def resolve(self, resolver):
        self.expression.resolve(resolver)

    
    def __str__(self):
        return f'print {self.expression}'


class Var(Stmt):
    def __init__(self, name, expression):
        self.name = name
        self.expression = expression

    
    def execute(self, interpreter):
        interpreter.environment.values[self.name] = self.expression.evaluate(interpreter) 
    

    def resolve(self, resolver):
        resolver.declare(self.name)
        if self.expression:
            self.expression.resolve(resolver)
        resolver.define(self.name)

    
    def __str__(self):
        return f'(dec {self.name} = {self.expression})'


class Block(Stmt):
    def __init__(self, statements):
        self.statements = statements
    
    def execute(self, interpreter):
        previous = interpreter.environment
        interpreter.environment = Environment(previous)
        
        for statement in self.statements:
            statement.execute(interpreter)
        
        interpreter.environment = previous
    

    def resolve(self, resolver):
        resolver.beginScope()
        for statement in self.statements:
            statement.resolve(resolver)
        resolver.endScope()

    
    def __str__(self):
        string = "\n"
        for statement in self.statements:
            string = string + str(statement) + '\n'
        return '{' + string + '}'


class If(Stmt):
    def __init__(self, condition, ifBranch, elseBranch):
        self.condition: Expr = condition
        self.ifBranch: Stmt = ifBranch
        self.elseBranch: Stmt = elseBranch


    def execute(self, interpreter):
        if self.condition.evaluate(interpreter):
            self.ifBranch.execute(interpreter)
        elif self.elseBranch:
            self.elseBranch.execute(interpreter)


    def resolve(self, resolver):
        self.condition.resolve(resolver)
        self.ifBranch.resolve(resolver)
        if self.elseBranch:
            self.elseBranch.resolve(resolver)


    def __str__(self):
        string = f'if {self.condition} {self.ifBranch}'
        if self.elseBranch != None:
            string += f'else {self.elseBranch}'
        return string
    

class While(Stmt):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    
    
    def execute(self, interpreter):
        while (self.condition.evaluate(interpreter)):
            self.body.execute(interpreter)
    
    
    def resolve(self, resolver):
        self.condition.resolve(resolver)
        self.body.resolve(resolver)
    

    def __str__(self):
        return f'while {self.condition}\n{self.body}'


class Function(Stmt):
    def __init__(self, name, parameters, body, kind):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.kind = kind
    

    def execute(self, interpreter):
        interpreter.environment.values[self.name] = LoxFunction(self, interpreter.environment)
    

    def resolve(self, resolver):
        resolver.declare(self.name)
        resolver.define(self.name)

        enclosingFunction = resolver.currentFunction
        resolver.currentFunction = self.kind

        resolver.beginScope()

        for parameter in self.parameters:
            resolver.declare(parameter.data)
            resolver.define(parameter.data)

        self.body.resolve(resolver)

        resolver.endScope()

        resolver.currentFunction = enclosingFunction


    def __str__(self):
        return f"<fn {self.name} {self.body}>"


class Return(Stmt):
    def __init__(self, keyword, value: Expr):
        self.keyword = keyword
        self.value = value
    

    def execute(self, interpreter):
        value = None
        if self.value != None:
            value = self.value.evaluate(interpreter)
        
        raise ReturnException(value)
    

    def resolve(self, resolver: Resolver) -> None:
        if resolver.currentFunction == "None":
            print("Can't return from top-level code.")
            exit(1)
        self.value.resolve(resolver)


    def __str__(self):
        return f"(return {self.value})j"


class Class(Stmt):
    def __init__(self, name, superclass, methods):
        self.name = name
        self.superclass = superclass
        self.methods = methods
    

    def execute(self, interpreter) -> None:
        superclass = None
        if self.superclass != None:
            superclass = self.superclass.evaluate(interpreter)
            if not isinstance(superclass, LoxClass):
                print("Superclass must be a class.")
                exit(1)

        interpreter.environment.values[self.name] = None

        if self.superclass != None:
            interpreter.environment = Environment(interpreter.environment)
            interpreter.environment.values['super'] = superclass

        methods = {}
        for method in self.methods:
            function = LoxFunction(method, interpreter.environment)
            methods[method.name] = function

        klass = LoxClass(self.name, superclass, methods)

        if self.superclass != None:
            interpreter.environment = interpreter.environment.enclosing

        interpreter.environment.values[self.name] = klass

    
    def resolve(self, resolver) -> None:
        resolver.declare(self.name)
        resolver.define(self.name)

        if self.superclass != None and self.superclass.name == self.name:
            print("A class can't inherit from itself.")
            exit(1)

        if self.superclass != None:
            self.superclass.resolve(resolver)

        if self.superclass != None:
            resolver.beginScope()
            resolver.scopes[-1]['super'] = True

        resolver.beginScope()
        resolver.scopes[-1]['this'] = True

        for method in self.methods:
            method.resolve(resolver)
        
        if self.superclass != None:
            resolver.endScope()

        resolver.endScope()

    
    def __str__(self):
        return f"(class {self.name})"