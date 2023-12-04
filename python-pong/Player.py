class Player:

    def __init__(self, name = "Player", binds = {"up" : "UNUSED_DEFAULT_KEY", 
    "down" : "UNUSED_DEFAULT_KEY", "left" : "UNUSED_DEFAULT_KEY", 
    "right" : "UNUSED_DEFAULT_KEY"}):
        self._name = name
        self._binds = binds
        self._score = 0

    def getScore(self):
        return self._score
    
    def getName(self):
        return self._name
    
    def getBinds(self):
        return self._binds
    
    def goal(self):
        self._score += 1

    def resetScore(self):
        self._score = 0
