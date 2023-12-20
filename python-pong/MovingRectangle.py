from abc import ABC, abstractmethod

class MovingRectangle:
	def __init__(self):
		pass

	# enclousure is NOT on the JS version of this, it is here to have values 
	# that are in the global canvas.height and canvas.width
	def initialize(self, dictCanvas: dict, name: str, position = {"x":0,"y":0}, speed = {"x":0, "y":0}, 
				size = {"x":0, "y":0}, enclousure = None):
		self._position = position
		self._speed = speed
		self._size = size
		self._dictCanvas = dictCanvas
		self.updateCorners()
		self._name = name
		self._dictCanvas[name] = {}
		if enclousure is None:
			self._enclousure = {"xl" : 0,"xh": 858,"yl": 0,"yh": 525}
		else:
			self._enclousure = enclousure
		

	def getPosition(self):
		return self._position
	
	def getSpeed(self):
		return self._speed
	
	def getSize(self):
		return self._size
	
	def getColor(self):
		return self._color
	
	def getCorners(self):
		return self._corners
	
	def getEnclousure(self):
		return self._enclousure
	
	def updateCorners(self):
		self._corners = {"xl":self.getPosition()["x"],
				   "xh": self.getPosition()["x"] + self.getSize()["x"],
				   "yl": self.getPosition()["y"],
				   "yh": self.getPosition()["y"] + self.getSize()["y"]}
	
	def setPosition(self, x = None, y = None):
		if x is None:
			x = self.getPosition()["x"] 
		if y is None:
			y = self.getPosition()["y"]
		self._position = {"x" : x, "y": y}
		self.updateCorners()

	def setSpeed(self, x = None, y = None):
		if x is None:
			x = self.getSpeed()["x"] 
		if y is None:
			y = self.getSpeed()["y"]
		self._speed = {"x" : x, "y": y}

	def setSize(self, x = None, y = None):
		if x is None:
			x = self.getSize()["x"] 
		if y is None:
			y = self.getSize()["y"]
		self._size = {"x" : x, "y": y}
   
	def setColor(self, color):
		self._color = color
    
	def draw(self):
		self._dictCanvas[self._name]["position"] = self.getPosition()
		self._dictCanvas[self._name]["size"] = self.getSize()
		self._dictCanvas[self._name]["speed"] = self.getSpeed()

	@abstractmethod
	def updatePosition(self):
		pass
    
