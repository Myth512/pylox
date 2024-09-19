class LoxInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}
    

    def get(self, name):
        if name in self.fields:
            return self.fields[name]
        
        method = self.klass.findMethod(name)

        if method != None:
            return method.bind(self)

        print(f"Undefined property {name}.")
        exit(1)
    

    def set(self, name, value):
        self.fields[name] = value


    def __str__(self):
        return f"instance of {self.klass.name}"
    