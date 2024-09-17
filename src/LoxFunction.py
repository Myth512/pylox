from LoxCallable import LoxCallable
from Environment import Environment
from ReturnException import ReturnException

class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure
    

    def call(self, interpreter, arguments):
        tmp = interpreter.environment
        interpreter.environment = Environment(self.closure)

        for i in range(len(self.declaration.parameters)):
            interpreter.environment.values[self.declaration.parameters[i].data] = arguments[i]
        
        try:
            self.declaration.body.execute(interpreter)
        except ReturnException as e:
            return e.value
        finally:
            interpreter.environment = tmp 
    

    def arity(self):
        return len(self.declaration.parameters)
    

    def bind(self, instance):
        environment = Environment(self.closure)
        environment.values['this'] = instance
        return LoxFunction(self.declaration, environment)


    def __str__(self):
        return f"<fn {self.declaration.name}>"
