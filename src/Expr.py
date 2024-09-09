from abc import ABC, abstractmethod
from Token import * 
from LoxCallable import LoxCallable
from Environment import *

class Expr(ABC):
    @abstractmethod
    def evaluate(self, environment):
        pass


class BinaryExpr(Expr):
    def __init__(self, left, operator, right):
        self.left: Expr = left
        self.operator: TokenType = operator
        self.right: Expr = right

    
    def evaluate(self, environment):
        left = self.left.evaluate(environment)
        right = self.right.evaluate(environment)

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

    
    def __str__(self):
        return f'({self.left} {self.operator.type.name} {self.right})'

    
class UnaryExpr(Expr):
    def __init__(self, operator, right):
        self.operator: TokenType = operator
        self.right: Expr = right

    
    def evaluate(self, environment):
        right = self.right.evaluate(environment)

        match(self.operator.type):
            case TokenType.MINUS:
                return -right
            case TokenType.BANG:
                return not right

    def __str__(self):
        return f'({self.operator.type.name} {self.right})'


class LiteralExpr(Expr):
    def __init__(self, value):
        self.value: float = value


    def evaluate(self, environment):
        return self.value if self.value != None else "nil"


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

    
    def evaluate(self, environment):
        match(self.operator.type):
            case TokenType.OR:
                return self.left.evaluate(environment) or self.right.evaluate(environment)
            case TokenType.AND:
                return self.left.evaluate(environment) and self.right.evaluate(environment)
    

    def __str__(self):
        return f'({self.left} {self.operator.type.name} {self.right})'

    
class GroupingExpr(Expr):
    def __init__(self, expression):
        self.expression: Expr = expression


    def evaluate(self, environment):
        return self.expression.evaluate(environment)

    
    def __str__(self):
        return f'({self.expression})'


class VarExpr(Expr):
    def __init__(self, name: str):
        self.name = name

    
    def evaluate(self, environment: Environment):
        if self.name in environment.values:
            value = environment.values[self.name]
            return value if value != None else 'nil' 
        elif environment.enclosing:
            value = self.evaluate(environment.enclosing)
            return value if value != None else 'nil' 
        print(f"Undefined variable {self.name}")
        exit(1)

    
    def __str__(self):
        return f'(var {self.name})'


class AssignExpr(Expr):
    def __init__(self, name, expression):
        self.name = name
        self.expression = expression
    

    def evaluate(self, environment):
        if self.name in environment.values:
            value = self.expression.evaluate(environment)
            environment.values[self.name] = value
            return value
        elif environment.enclosing:
            self.evaluate(environment.enclosing)
        else:
            print(f"Undeclared variable {self.name}")
            exit(1)
    

    def __str__(self):
        return f'(assign {self.name} = {self.expression})'


class CallExpr(Expr):
    def __init__(self, callee, paren, arguments):
        self.callee: Expr = callee
        self.paren: Token = paren
        self.arguments: list[Expr] = arguments


    def evaluate(self, environment):
        callee = self.callee.evaluate(environment)
        if not isinstance(callee, LoxCallable):
            print("Can only call functions and classes.")
            exit(1)

        arguments = []
        for argument in self.arguments:
            arguments.append(argument.evaluate(environment))

        if len(arguments) != callee.arity():
            print(f"Expected {callee.arity()} arguments but got {len(arguments)}.") 
            exit(1)
        return callee.call(environment, arguments)
    

