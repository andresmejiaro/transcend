from MovingRectangle import MovingRectangle

class Paddle(MovingRectangle):

	def __init__(self, dictCanvas: dict, name:str, keyboard: dict,
			position ={"x" : 30,"y" : 0}, speed = {"x" : 10, "y" : 10},
			size = {"x" : 10, "y" : 30}, 
			binds = {"up" : "UNUSED_DEFAULT_KEY", "down" : "UNUSED_DEFAULT_KEY",
			"left" : "UNUSED_DEFAULT_KEY", "right" : "UNUSED_DEFAULT_KEY"}, 
			enclousure = None):
		self.initialize(dictCanvas = dictCanvas, name = name, 
				   position = position, speed = speed, size = size,
						 enclousure = enclousure)
		self._binds = binds
		self._maxSpeed = speed
		self._keyboard = keyboard
		for value in binds.values():
			self._keyboard[value] = False

	def getMaxSpeed(self):
		return self._maxSpeed
	
	def updatePosition(self):
		xSpeed = (self._keyboard[self._binds["right"]] - 
			self._keyboard[self._binds["left"]]) * self.getMaxSpeed()["x"]
		ySpeed = (self._keyboard[self._binds["down"]] - 
			self._keyboard[self._binds["up"]]) * self.getMaxSpeed()["y"]
		if not isinstance(xSpeed, (int, float)):
			xSpeed = 0
		if not isinstance(ySpeed, (int, float)):
			ySpeed = 0
		if xSpeed < 0 and self.getPosition()["x"] <= self.getEnclousure()["xl"]:
			xSpeed = 0
		if ySpeed < 0 and self.getPosition()["y"] <= self.getEnclousure()["yl"]:
			ySpeed = 0
		if (xSpeed > 0 and self.getPosition()["x"] + self.getSize()["x"] 
				>= self.getEnclousure()["xh"]):
			xSpeed = 0
		if (ySpeed > 0 and self.getPosition()["y"] + self.getSize()["y"] 
				>= self.getEnclousure()["yh"]):
			ySpeed = 0
		xNewPos = self.getPosition()["x"] + xSpeed
		if (xNewPos < self.getEnclousure()["xl"]):
			xNewPos = self.getEnclousure()["xl"]
		if (xNewPos + self.getSize()["x"] > self.getEnclousure()["xh"]):
			xNewPos = self.getEnclousure()["xh"] - self.getSize()["x"]
		yNewPos = self.getPosition()["y"] + ySpeed
		if (yNewPos < self.getEnclousure()["yl"]):
			yNewPos = self.getEnclousure()["yl"]
		if (yNewPos + self.getSize()["y"] > self.getEnclousure()["yh"]):
			yNewPos = self.getEnclousure()["yh"] - self.getSize()["y"]
		self.setPosition(x = xNewPos, y = yNewPos)
		self.setSpeed(x = xSpeed, y = ySpeed)

		