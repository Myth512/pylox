class Environment():
    def __init__(self, enclosing = None):
        self.values = {}
        self.enclosing = enclosing
    