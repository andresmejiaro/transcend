from Player import Player
from Ball import Ball
from Paddle import Paddle
import random
import time
import threading


class Game:
	def __init__(self, dictKeyboard: dict, 
				 leftPlayer: Player, rightPlayer: Player, enclousure = None):
		self._leftPlayer = leftPlayer
		self._rightPlayer = rightPlayer
		self._scoreLimit = 11
		self._dictCanvas = {}
		self._dictKeyboard = dictKeyboard
		self._scoreReporter = {}
		if enclousure is None:
				self._enclousure = {"xl" : 0,"xh": 858,"yl": 0,"yh": 525}
		else:
			self._enclousure = enclousure
		self._ball = Ball(dictCanvas = self._dictCanvas, 
			name ="ball",
			position = {"x": 0,	"y":0}, speed = {"x" : 0, "y" : 0},
				size = {"x" : 10, "y" : 10})
		self.resetPosition()
		self._leftPaddle = Paddle(keyboard=self._dictKeyboard,
			dictCanvas = self._dictCanvas, name = "leftPaddle",
							position= {"x" : self._enclousure["xl"] + 30, 
				  "y" : self._enclousure["yl"]}, speed = {"x" : 10, "y": 10}, 
				  size = {"x":10, "y":100}, binds = self._leftPlayer.getBinds(),
				    enclousure=self._enclousure)
		self._rightPaddle = Paddle(keyboard=self._dictKeyboard,
							 dictCanvas = self._dictCanvas, name = "rightPaddle",
							position= {"x" : self._enclousure["xh"] - 30, 
				  "y" : self._enclousure["yl"] }, speed = {"x" : 10, "y": 10}, 
				  size = {"x":10, "y":100}, binds = self._rightPlayer.getBinds(),
				    enclousure=self._enclousure)
		self._rightPlayer.resetScore()
		self._leftPlayer.resetScore()
		self._ball.addColider(self._leftPaddle)
		self._ball.addColider(self._rightPaddle)
		self.resetPosition()
		self.reportScore()


	def reportScore(self):
		self._scoreReporter[self._leftPlayer.getName()] = self._leftPlayer.getScore()
		self._scoreReporter[self._rightPlayer.getName()] = self._rightPlayer.getScore()
		return self._scoreReporter.copy()

	def recievePaddle(self, data):
		for (key, value) in data.items:
			if (key == "leftPaddle"):
				self._leftPaddle.setPosition(x = value["position"]["x"], y = value["position"]["y"])
				self._leftPaddle.setSpeed(x = value["speed"]["x"], y = value["speed"]["y"])
			if (key == "rightPaddle"):
				self._rightPaddle.setPosition(x = value["position"]["x"], y = value["position"]["y"])
				self._rightPaddle.setSpeed(x = value["speed"]["x"], y = value["speed"]["y"])


	def pointLoop(self):
		self._ball.draw()
		ballState = self._ball.updatePosition()
		if ballState == 1:
			self._leftPlayer.goal()
			self.reportScore()
			self.resetPosition()
		elif ballState == -1:
			self._rightPlayer.goal()
			self.reportScore()
			self.resetPosition()
		else:
			self._leftPaddle.draw()
			self._leftPaddle.updatePosition()
			self._rightPaddle.draw()
			self._rightPaddle.updatePosition()
		
		

	def resetPosition(self):
		self._ball.setPosition(x = (self._enclousure["xl"] + 
							   self._enclousure["xh"])/2, y = (self._enclousure["yl"] + 
							   self._enclousure["yh"])/2)
		ran = random.uniform(0,1)
		if ran < 0.25:
			self._ball.setSpeed(x = 4, y = 1)
		elif ran < 0.5:
			self._ball.setSpeed(x = -4, y = 1)
		elif ran < 0.75:
			self._ball.setSpeed(x = 4, y = -1)
		else:
			self._ball.setSpeed(x = -4, y = -1)

	def start2(self):
		fps = 60
		frame_dur = 1 / fps
		while(self._leftPlayer.getScore() < self._scoreLimit and 
			self._rightPlayer.getScore() < self._scoreLimit):
			start_time = time.time()
			self.pointLoop()
			elapsed_time = time.time() -start_time
			tsleep = frame_dur - elapsed_time
			if tsleep > 0:
				time.sleep(tsleep)

	def start(self):
		self._bgt = threading.Thread(target = self.start2)
		self._bgt.start()

	def reportScreen(self):
		return self._dictCanvas.copy()
	
	
	def isAlive(self):
		try:
			return self._bgt.is_alive()
		except:
			return 0
		

	

