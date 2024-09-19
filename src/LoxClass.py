from LoxCallable import LoxCallable
from LoxInstance import LoxInstance


class LoxClass(LoxCallable):
    def __init__(self, name, superclass, methods):
        self.name = name
        self.superclass = superclass
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
    

    def findMethod(self, name):
        if name in self.methods:
            return self.methods[name]
        
        if self.superclass != None:
            return self.superclass.findMethod(name)
    

    def __str__(self):
        return f"(class {self.name} inherit from {self.superclass})"
        