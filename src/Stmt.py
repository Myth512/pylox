from abc import ABC, abstractmethod
from Expr import *
from LoxFunction import LoxFunction 
from ReturnException import ReturnException

class Stmt:
    @abstractmethod
    def execute(self):
        pass


class Expression(Stmt):
    def __init__(self, expression):
        self.expression: Expr = expression

    
    def execute(self, environment):
        return self.expression.evaluate(environment)


    def __str__(self):
        return f'expr {self.expression}'


class Print(Stmt):
    def __init__(self, expression):
        self.expression: Expr = expression

    
    def execute(self, environment):
        print(self.expression.evaluate(environment))

    
    def __str__(self):
        return f'print {self.expression}'


class Var(Stmt):
    def __init__(self, name, expression):
        self.name = name
        self.expression = expression

    
    def execute(self, environment):
        environment.values[self.name] = self.expression.evaluate(environment) 

    
    def __str__(self):
        return f'(dec {self.name} = {self.expression})'


class Block(Stmt):
    def __init__(self, statements):
        self.statements = statements
    
    def execute(self, environment):
        previous = environment
        environment = Environment(previous)
        
        for statement in self.statements:
            statement.execute(environment)
        
        environment = previous
    
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


    def execute(self, environment):
        if self.condition.evaluate(environment):
            self.ifBranch.execute(environment)
        elif self.elseBranch:
            self.elseBranch.execute(environment)


    def __str__(self):
        string = f'if {self.condition} {self.ifBranch}'
        if self.elseBranch != None:
            string += f'else {self.elseBranch}'
        return string
    

class While(Stmt):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    
    
    def execute(self, environment):
        while (self.condition.evaluate(environment)):
            self.body.execute(environment)
    

    def __str__(self):
        return f'while {self.condition}\n{self.body}'


class Function(Stmt):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body
    

    def execute(self, environment):
        environment.values[self.name] = LoxFunction(self)
    

    def __str__(self):
        return f"<fn {self.name}>"


class Return(Stmt):
    def __init__(self, keyword, value: Expr):
        self.keyword = keyword
        self.value = value
    

    def execute(self, environment):
        value = None
        if self.value != None:
            value = self.value.evaluate(environment)
        
        raise ReturnException(value)


    def __str__(self):
        return f"(return {self.value})"