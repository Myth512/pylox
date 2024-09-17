from Expr import *
from Token import *
from Stmt import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    
    def error(self, message):
        print(message)
        exit(1)


    def reachEnd(self) -> bool:
        return self.current >= len(self.tokens)

    
    def previous(self) -> str:
        return self.tokens[self.current - 1]


    def advance(self) -> str:
        if not self.reachEnd():
            self.current += 1
        return self.previous()


    def peek(self) -> str:
        return self.tokens[self.current]


    def check(self, type: TokenType) -> bool:
        if self.reachEnd():
            return False
        return self.peek().type == type


    def match(self, *types: TokenType) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    
    def consume(self, type, message: str) -> str:
        if self.check(type):
            return self.advance()
        self.error(message)

    
    def parse(self) -> list[Stmt]:
        statements = []
        while not self.reachEnd():
            statements.append(self.declaration())
        
        return statements

    
    def declaration(self):
        if self.match(TokenType.VAR):
            return self.varDeclaration()
        if self.match(TokenType.FUN):
            return self.function("function")
        if self.match(TokenType.CLASS):
            return self.classDeclaration()
        return self.statement()


    def varDeclaration(self):
        name: str = self.consume(TokenType.IDENTIFIER, "Expect variable name.").data

        value = None
        if self.match(TokenType.EQUAL):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, value)


    def function(self, kind) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.").data
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")

        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
            while self.match(TokenType.COMMA):
                if len(parameters) >= 255:
                    print("Can't have more than 255 parameters.")
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
            
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")

        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block()
        return Function(name, parameters, body, kind)
    

    def classDeclaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.").data
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.reachEnd():
            methods.append(self.function("method"))
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
    
        return Class(name, methods)


    def statement(self) -> Stmt:
        if self.match(TokenType.IF):
            return self.ifStmt()
        if self.match(TokenType.WHILE):
            return self.whileStmt()
        if self.match(TokenType.FOR):
            return self.forStmt()
        if self.match(TokenType.PRINT):
            return self.printStmt()
        if self.match(TokenType.RETURN):
            return self.returnStmt()
        if self.match(TokenType.LEFT_BRACE):
            return self.block()
        return self.exprStmt()


    def ifStmt(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if conditions.")

        ifBranch = self.statement()
        elseBranch = None
        if self.match(TokenType.ELSE):
            elseBranch = self.statement()

        return If(condition, ifBranch, elseBranch)


    def whileStmt(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after while statement.")

        body = self.statement()

        return While(condition, body)
    

    def forStmt(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer = None
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.varDeclaration()
        else:
            initializer = self.exprStmt()

        condition = None 
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after the condition.")
        
        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = Expression(self.expression())
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for loop.")

        body = self.statement()

        if increment:
            body = Block([body, increment])

        if not condition:
            condition = LiteralExpr(True) 
        body = While(condition, body)

        if initializer:
            body = Block([initializer, body])
        
        return body
    

    def printStmt(self) -> Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)


    def returnStmt(self) -> Stmt:
        keyword = self.previous()

        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")

        return Return(keyword, value)


    def block(self) -> Stmt:
        statements = []

        while (not self.reachEnd()) and (not self.check(TokenType.RIGHT_BRACE)):
            statements.append(self.declaration())
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")

        return Block(statements)


    def exprStmt(self) -> Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, f"Expect ';' after expression. {expr}")
        return Expression(expr)


    def expression(self) -> Expr:
        return self.assignment()


    def assignment(self) -> Expr:
        expr = self.lor()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, VarExpr):
                name = expr.name
                return AssignExpr(name, value)
            elif isinstance(expr, GetExpr):
                return SetExpr(expr.obj, expr.name, value)
            
            print(equals, "Invalid assignment target")
            exit(1)
        
        return expr


    def lor(self) -> Expr:
        expr = self.land()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.land()
            expr = LogicalExpr(expr, operator, right)
        
        return expr
    

    def land(self) -> Expr:
        expr = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = LogicalExpr(expr, operator, right)
        
        return expr
    

    def equality(self) -> Expr:
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = BinaryExpr(expr, operator, right)
        
        return expr


    def comparison(self) -> Expr:
        expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = BinaryExpr(expr, operator, right)
        
        return expr


    def term(self) -> Expr:
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS, TokenType.MOD):
            operator = self.previous()
            right = self.factor()
            expr = BinaryExpr(expr, operator, right)
        
        return expr


    def factor(self) -> Expr:
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = BinaryExpr(expr, operator, right)
        
        return expr


    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return UnaryExpr(operator, right)
        
        return self.call()


    def call(self) -> Expr:
        expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finishCall(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.").data
                expr = GetExpr(expr, name)
            else:
                break
        
        return expr


    def finishCall(self, callee: Expr) -> Expr:
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                if len(arguments) >= 255:
                    print("Can't have more than 255 arguments.")
                arguments.append(self.expression())

        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return CallExpr(callee, paren, arguments)


    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return LiteralExpr(False)
        if self.match(TokenType.TRUE):
            return LiteralExpr(True)
        if self.match(TokenType.NIL):
            return LiteralExpr(None)
        if self.match(TokenType.IDENTIFIER):
            return VarExpr(self.previous().data)
        if self.match(TokenType.THIS):
            return ThisExpr(self.previous())
        
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self.previous().data)
        
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return GroupingExpr(expr)
    