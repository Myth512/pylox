from LoxCallable import LoxCallable
from LoxInstance import LoxInstance


class LoxClass(LoxCallable):
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods
    

    def call(self, envitonment, arguments):
        instance = LoxInstance(self)
        if "init" in self.methods:
            self.methods["init"].bind(instance).call(envitonment, arguments)
        return instance
    

    def arity(self):
        if "init" in self.methods:
            return self.methods["init"].arity()
        return 0 