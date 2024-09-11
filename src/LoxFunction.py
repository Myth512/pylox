from LoxCallable import LoxCallable
from Environment import Environment
from ReturnException import ReturnException

class LoxFunction(LoxCallable):
    def __init__(self, declaration):
        self.declaration = declaration
    

    def call(self, environment, arguments):
        newEnvironment = Environment(environment)

        for i in range(len(self.declaration.parameters)):
            newEnvironment.values[self.declaration.parameters[i].data] = arguments[i]
        
        try:
            self.declaration.body.execute(newEnvironment)
        except ReturnException as e:
            return e.value
    

    def arity(self):
        return len(self.declaration.parameters)
    

    def __str__(self):
        return f"<fn {self.declaration.name}>"
