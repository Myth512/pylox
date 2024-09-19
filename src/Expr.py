from abc import ABC, ABCMeta, abstractmethod
from Token import * 
from LoxCallable import LoxCallable
from Environment import *
from LoxInstance import LoxInstance

class Expr(ABC):
    @abstractmethod
    def evaluate(self, interpreter):
        pass


    @abstractmethod
    def resolve(self, resolver):
        pass


class BinaryExpr(Expr):
    def __init__(self, left, operator, right):
        self.left: Expr = left
        self.operator: TokenType = operator
        self.right: Expr = right

    
    def evaluate(self, interpreter):
        left = self.left.evaluate(interpreter)
        right = self.right.evaluate(interpreter)

        match(self.operator.type):
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return left + right 
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                print(f"Type error, unsupported operator {self.operator.type.name} for operand types {type(left)} and {type(right)}")
                exit(1)
            case TokenType.MINUS:
                return left - right
            case TokenType.STAR:
                return left * right
            case TokenType.SLASH:
                return left / right
            case TokenType.MOD:
                return left % right;
            case TokenType.GREATER:
                return left > right
            case TokenType.GREATER_EQUAL:
                return left >= right
            case TokenType.LESS:
                return left < right
            case TokenType.LESS_EQUAL:
                return left <= right
            case TokenType.EQUAL_EQUAL:
                return left == right
            case TokenType.BANG_EQUAL:
                return left != right


    def resolve(self, resolver):
        self.left.resolve(resolver)
        self.right.resolve(resolver)
    
    def __str__(self):
        return f'({self.left} {self.operator.type.name} {self.right})'

    
class UnaryExpr(Expr):
    def __init__(self, operator, right):
        self.operator: TokenType = operator
        self.right: Expr = right

    
    def evaluate(self, interpreter):
        right = self.right.evaluate(interpreter)

        match(self.operator.type):
            case TokenType.MINUS:
                return -right
            case TokenType.BANG:
                return not right
    

    def resolve(self, resolver):
        self.right.resolve(resolver)

    def __str__(self):
        return f'({self.operator.type.name} {self.right})'


class LiteralExpr(Expr):
    def __init__(self, value):
        self.value = value


    def evaluate(self, interpreter):
        return self.value if self.value != None else "nil"


    def resolve(self, resolver):
        return

    def __str__(self):
        if self.value == None:
            return 'nil'
        elif isinstance(self.value, str):
            return f'"{self.value}"'
        return f'({self.value})'


class LogicalExpr(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    
    def evaluate(self, interpeter):
        match(self.operator.type):
            case TokenType.OR:
                return self.left.evaluate(interpeter) or self.right.evaluate(interpeter)
            case TokenType.AND:
                return self.left.evaluate(interpeter) and self.right.evaluate(interpeter)
    
    
    def resolve(self, resolver):
        self.left.resolve(resolver)
        self.right.resolve(resolver)
    

    def __str__(self):
        return f'({self.left} {self.operator.type.name} {self.right})'

    
class GroupingExpr(Expr):
    def __init__(self, expression):
        self.expression: Expr = expression


    def evaluate(self, interpeter):
        return self.expression.evaluate(interpeter)
    

    def resolve(self, resolver):
        self.expression.resolve(resolver)

    
    def __str__(self):
        return f'({self.expression})'


class VarExpr(Expr):
    def __init__(self, name: str):
        self.name = name

    
    def evaluate(self, interpreter):
        return interpreter.lookUpVar(self.name, self)
    
    
    def resolve(self, resolver):
        if resolver.scopes[-1].get(self.name, True) == False:
            print("Can't use variable in its own declaration.")
            exit(1)
        resolver.resolveLocal(self, self.name)

    
    def __str__(self):
        return f'(var {self.name})'


class AssignExpr(Expr):
    def __init__(self, name, expression):
        self.name = name
        self.expression = expression
    

    def evaluate(self, interpreter):
        dist = interpreter.locals[self]
        value = self.expression.evaluate(interpreter)
        interpreter.environment.assignAt(dist, self.name, value)
    

    def resolve(self, resolver):
        self.expression.resolve(resolver)
        resolver.resolveLocal(self, self.name)


    def __str__(self):
        return f'(assign {self.name} = {self.expression})'


class CallExpr(Expr):
    def __init__(self, callee, paren, arguments):
        self.callee: Expr = callee
        self.paren: Token = paren
        self.arguments: list[Expr] = arguments


    def evaluate(self, interpeter):
        callee = self.callee.evaluate(interpeter)
        if not isinstance(callee, LoxCallable):
            print("Can only call functions and classes.")
            exit(1)

        arguments = []
        for argument in self.arguments:
            arguments.append(argument.evaluate(interpeter))

        if len(arguments) != callee.arity():
            print(f"Expected {callee.arity()} arguments but got {len(arguments)}.") 
            exit(1)
        return callee.call(interpeter, arguments)
    

    def resolve(self, resolver):
        self.callee.resolve(resolver)

        for arg in self.arguments:
            arg.resolve(resolver)

        for i in range(len(resolver.scopes) - 1, -1, -1):
            if self.callee.name in resolver.scopes[i]:
                resolver.interpreter.resolve(self, len(resolver.scopes) - i - 1)
                return
    

    def __str__(self):
        return "call"
    

class GetExpr(Expr):
    def __init__(self, obj, name):
        self.obj = obj
        self.name = name
    

    def evaluate(self, interpreter):
        obj = self.obj.evaluate(interpreter)
        if isinstance(obj, LoxInstance):
            return obj.get(self.name)
        print("Only instances have properties.")
        exit(1)
    

    def resolve(self, resolver):
        self.obj.resolve(resolver)
    

    def __str__(self):
        return f"(get {self.name})"


class SetExpr(Expr):
    def __init__(self, obj, name, value):
        self.obj = obj
        self.name = name
        self.value = value
    

    def evaluate(self, interpreter):
        obj = self.obj.evaluate(interpreter)

        if not isinstance(obj, LoxInstance):
            print("Only instances have fields.")
            exit(1)
        
        value = self.value.evaluate(interpreter)
        obj.set(self.name, value)
        return value
    

    def resolve(self, resolver):
        self.obj.resolve(resolver)
        self.value.resolve(resolver)
    

    def __str__(self):
        return f"(set {self.name})"


class ThisExpr(Expr):
    def __init__(self, keyword):
        self.keyword = keyword
    

    def evaluate(self, interpreter):
        return interpreter.lookUpVar('this', self.keyword)
    
    
    def resolve(self, resolver):
        if resolver.currentFunction != 'method':
            print("Can't use 'this' outside of a class.")
            exit(1)
        resolver.resolveLocal(self.keyword, 'this')
    

    def __str__(self):
        return f"(this {self.keyword})"


class SuperExpr(Expr):
    def __init__(self, keyword, method):
        self.keyword = keyword
        self.name = 'super'
        self.method = method
    

    def evaluate(self, interpreter):
        distance = interpreter.locals[self.keyword]
        superclass = interpreter.environment.getAt(distance, 'super')
        obj = interpreter.environment.getAt(distance - 1, 'this')
        method = superclass.findMethod(self.method.data)

        if method == None:
            print(f"Undefined property {method}.")
            exit(1)
        
        return method.bind(obj)
    

    def resolve(self, resolver):
        # print("DEBUG: SuperExpr resolve()")
        resolver.resolveLocal(self.keyword, 'super')
    

    def __str__(self):
        return f"(super {self.keyword})"