from LoxCallable import LoxCallable
from LoxInstance import LoxInstance


class LoxClass(LoxCallable):
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods
    

    def call(self, envitonment, arguments):
        return LoxInstance(self)
    

    def arity(self):
        return 0 