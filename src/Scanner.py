import sys
from Token import *

class Scanner:
    def __init__(self, source: str):
        self.source: str = source
        self.tokens: list[Token] = []
        self.start: int = 0
        self.current: int = 0
        self.line: int = 1
        self.keywords = {
            "and"       : TokenType.AND,
            "class"     : TokenType.CLASS,
            "else"      : TokenType.ELSE,
            "false"     : TokenType.FALSE,
            "if"        : TokenType.IF,
            "for"       : TokenType.FOR,
            "fun"       : TokenType.FUN,
            "nil"       : TokenType.NIL,
            "or"        : TokenType.OR,
            "print"     : TokenType.PRINT,
            "return"    : TokenType.RETURN,
            "super"     : TokenType.SUPER,
            "this"      : TokenType.THIS,
            "true"      : TokenType.TRUE,
            "var"       : TokenType.VAR,
            "while"     : TokenType.WHILE
        }


    def reachEnd(self) -> bool:
        return self.current >= len(self.source)


    def advance(self) -> str:
        if self.reachEnd():
            return '\0'
        c = self.source[self.current] 
        self.current += 1
        return c


    def peek(self) -> str:
        if self.reachEnd():
            return '\0'
        return self.source[self.current]

    
    def peekNext(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current+1]


    def match(self, expected: str) -> bool:
        if self.peek() != expected:
            return False
        self.current += 1
        return True 

    
    def isValidIdentifierChar(self, c: str) -> bool:
        return c.isalpha() or c.isdigit() or c == '_'

    
    def addToken(self, type: TokenType, data: any = None) -> None:
        self.tokens.append(Token(type, data, self.line))


    def scan(self):
        while not self.reachEnd():
            self.start = self.current
            self.scanToken()

        # self.addToken(TokenType.EOF)

        return self.tokens;
    

    def scanToken(self):
        c = self.advance()
        match c:
            case '(':
                self.addToken(TokenType.LEFT_PAREN)
            case ')':
                self.addToken(TokenType.RIGHT_PAREN)
            case '{':
                self.addToken(TokenType.LEFT_BRACE)
            case '}':
                self.addToken(TokenType.RIGHT_BRACE)
            case ',':
                self.addToken(TokenType.COMMA)
            case '.':
                self.addToken(TokenType.DOT)
            case '-':
                self.addToken(TokenType.MINUS)
            case '+':
                self.addToken(TokenType.PLUS)
            case ';':
                self.addToken(TokenType.SEMICOLON)
            case '*':
                self.addToken(TokenType.STAR)
            case '%':
                self.addToken(TokenType.MOD)
            case '!':
                if self.match('='):
                    self.addToken(TokenType.BANG_EQUAL)
                else:
                    self.addToken(TokenType.BANG)
            case '=':
                if self.match('='):
                    self.addToken(TokenType.EQUAL_EQUAL)
                else:
                    self.addToken(TokenType.EQUAL)
            case '<':
                if self.match('='):
                    self.addToken(TokenType.LESS_EQUAL)
                else:
                    self.addToken(TokenType.LESS)
            case '>':
                if self.match('='):
                    self.addToken(TokenType.GREATER_EQUAL)
                else:
                    self.addToken(TokenType.GREATER)
            case '/':
                if self.match('/'):
                    while self.peek() != '\n' and not self.reachEnd():
                        self.advance()
                else:
                    self.addToken(TokenType.SLASH)
            case ' ':
                pass
            case '\r':
                pass
            case '\t':
                pass
            case '\n':
                self.line += 1
            case '"':
                self.scanString()
            case _:
                if c.isdigit():
                    self.scanNumber()
                elif c.isalpha or c == '_':
                    self.scanIdentifier()
                else:
                    print("Unexpected token")
                    sys.exit(1)


    def scanNumber(self) -> None:
        while self.peek().isdigit():
            self.advance()
        if self.peek() == '.':
            if self.peekNext().isdigit():
                self.advance()
            else:
                print("Unexpected decimal point")
                exit(1)
            
            while self.peek().isdigit():
                self.advance()
        self.addToken(TokenType.NUMBER, float(self.source[self.start:self.current]))


    def scanString(self) -> None:
        while self.peek() != '"' and not self.reachEnd():
            if self.peek() == '\n':
                self.line += 1
            self.advance()

            if self.reachEnd():
                print("Untermenated string on line ", self.line)
                sys.exit(1)
            
        data = self.source[self.start+1:self.current]
        self.addToken(TokenType.STRING, data)
        self.advance()

        
    def scanIdentifier(self) -> None:
        while self.isValidIdentifierChar(self.peek()):
            self.advance()
        identifier = self.source[self.start:self.current]
        type = self.keywords.get(identifier, None)
        if type != None:
            self.addToken(type)
        else:
            self.addToken(TokenType.IDENTIFIER, identifier)
