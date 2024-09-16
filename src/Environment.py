class Environment():
    def __init__(self, enclosing = None):
        self.values = {}
        self.enclosing = enclosing


    def getAt(self, dist, name): 
        return self.ancestor(dist).values[name]


    def assignAt(self, dist, name, value):
        self.ancestor(dist).values[name] = value


    def ancestor(self, dist):
        environment = self

        for _ in range(dist):
            environment = environment.enclosing
        
        return environment