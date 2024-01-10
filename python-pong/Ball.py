from MovingRectangle import MovingRectangle

class Ball(MovingRectangle):
	# enclousure is NOT on the JS version of this, it is here to have values 
	# that are in the global canvas.height and canvas.width
	def __init__(self, dictCanvas: dict, name: str,
			  position = {"x" : 0, "y" : 0}, speed = {"x" :0, "y" : 0},
			  size = {"x" : 0, "y" : 0}, enclousure = None):
		self.initialize(dictCanvas = dictCanvas, name = name,
				   position = position,speed = speed, 
				   size = size, enclousure = enclousure)
		self._collide = []
		

	def checkCollision(self, colider: MovingRectangle) -> bool:
		# Check if upper right corner is touching the collider
		if (colider.getCorners()["xl"] <= self.getCorners()["xl"] and 
			self.getCorners()["xl"] <= colider.getCorners()["xh"] and
			colider.getCorners()["yl"] <= self.getCorners()["yl"] and
			self.getCorners()["yl"] <= colider.getCorners()["yh"]):
			return True

		#Check if upper left corner is touching the collider
		if (colider.getCorners()["xl"] <= self.getCorners()["xh"] and 
			self.getCorners()["xh"] <= colider.getCorners()["xh"] and
			colider.getCorners()["yl"] <= self.getCorners()["yl"] and
			self.getCorners()["yl"] <= colider.getCorners()["yh"]):
			return True

		#// Check if lower right corner is touching the collider
		if (colider.getCorners()["xl"] <= self.getCorners()["xl"] and 
			self.getCorners()["xl"] <= colider.getCorners()["xh"] and
			colider.getCorners()["yl"] <= self.getCorners()["yh"] and
			self.getCorners()["yh"] <= colider.getCorners()["yh"]):
			return True
        
		#// Check if lower left corner is touching the collider
		if (colider.getCorners()["xl"] <= self.getCorners()["xh"] and 
			self.getCorners()["xh"] <= colider.getCorners()["xh"] and
			colider.getCorners()["yl"] <= self.getCorners()["yh"] and
			self.getCorners()["yh"] <= colider.getCorners()["yh"]):
			return True
		return False
	
	def collisionHandler(self, colider: MovingRectangle):
		#//Calculate the left and right side of the "inscribed square of the intersection"
		leftInter = max(self.getCorners()["xl"],colider.getCorners()["xl"])
		rightInter = min(self.getCorners()["xh"],colider.getCorners()["xh"])
		# calculate the proportion of the movement that overlaps
		adj = abs(leftInter - rightInter)/abs(self.getSpeed()["x"])
		# undo overlaping
		self.setPosition(x = self.getPosition()["x"] - adj * self.getSpeed()["x"],
				   y = self.getPosition()["y"] - adj * self.getSpeed()["y"])
		#calculate the nearest side and consider that colision from that dir
		x1 = abs(self.getCorners()["xl"] - colider.getCorners()["xh"])
		x2 = abs(self.getCorners()["xh"] - colider.getCorners()["xl"])
		y1 = abs(self.getCorners()["yl"] - colider.getCorners()["yh"])
		y2 = abs(self.getCorners()["yh"] - colider.getCorners()["yl"])
		if min(x1,x2) < min(y1,y2):
			self.setSpeed(x = -self.getSpeed()["x"], 
				  y = self.getSpeed()["y"] + 0.5 * colider.getSpeed()["y"])
		else:
			self.setSpeed(y = -self.getSpeed()["y"])
		
	def updatePosition(self) ->int:
		if (self.getPosition()["x"] + self.getSize()["x"] >= 
	  			self.getEnclousure()["xh"]):
			self.setSpeed(x = -self.getSpeed()["x"])
			return 1
		if (self.getPosition()["x"] < self.getEnclousure()["xl"]):
			self.setSpeed(x = -self.getSpeed()["x"])
			return -1
		if (self.getPosition()["y"] + self.getSize()["y"] > 
	  			self.getEnclousure()["yh"] 
				or self.getPosition()["y"] < self.getEnclousure()["yl"]):
			self.setSpeed(y = -self.getSpeed()["y"])
		for ele in self._collide:
			if (self.checkCollision(ele)):
				self.collisionHandler(ele)
		self.setPosition(x = self.getPosition()["x"] + self.getSpeed()["x"],
				   y = self.getPosition()["y"] + self.getSpeed()["y"])
		return 0
	
	def addColider(self,colider):
		self._collide.append(colider)
