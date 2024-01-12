from .Player import Player
from .Ball import Ball
from .Paddle import Paddle
import random
import time
import threading


class Game:
	def __init__(self, dictKeyboard: dict, 
				 leftPlayer: Player, rightPlayer: Player, enclousure = None, scoreLimit = 10):
		self._leftPlayer = leftPlayer
		self._rightPlayer = rightPlayer
		self._scoreLimit = int(scoreLimit)
		self._dictPaddleCommands = {}
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
		self._frame = 0
		self._delayedActions = {}


	def reportScore(self):
		self._scoreReporter[self._leftPlayer.getName()] = self._leftPlayer.getScore()
		self._scoreReporter[self._rightPlayer.getName()] = self._rightPlayer.getScore()
		return self._scoreReporter.copy()


	def pointLoop(self):
		self.runDelayedActions()
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
		self._frame += 1
  
	def pointLoop2(self):
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
		self._frame += 1
		
		

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
		try:
			fps = 60
			if fps < 1 or fps > 60 or type(fps) != int:
				fps = 60
			frame_dur = 1/fps
			while self._leftPlayer.getScore() < self._scoreLimit and self._rightPlayer.getScore() < self._scoreLimit:
				start_time = time.time()
				self.pointLoop()
				elapsed_time = time.time() - start_time
				tsleep = frame_dur - elapsed_time
				if tsleep > 0:
					time.sleep(tsleep)
				else:
					print("I'm taking too long")
		except Exception as e:
			print(f"Exception in game loop: {e}")

	def start(self):
		print("Starting game")
		self._bgt = threading.Thread(target = self.start2)
		self._bgt.start()

	def stop(self):
		print("Stopping game")
		self._bgt._scoreLimit = 0

	def reportFrame(self):
		return self._frame

	def reportScreen(self):
		return self._dictCanvas.copy()
	
	def isAlive(self):
		try:
			return self._bgt.is_alive()
		except:
			return 0
		
	def processInput(self, formatted_key, is_pressed,frame):
		diff_frames = self._frame - frame
		print(formatted_key)
		print(self._rightPaddle._binds)
		if (diff_frames > 0):
			print("fast forwarding")
			self._dictKeyboard[formatted_key] = is_pressed
			if (formatted_key in self._leftPaddle._binds):
				for j in range(diff_frames):
					self._leftPaddle.updatePosition()
			elif (formatted_key in self._rightPaddle._binds):
				for j in range(diff_frames):
					self._rightPaddle.updatePosition()
		elif diff_frames == 0:
			self._dictKeyboard[formatted_key] = is_pressed
		else:
			self.addDelayedAction(frame, self.processInput,formatted_key, is_pressed, frame)
			
	
	def addDelayedAction(self, frame, function, *args, **kwargs):
		if frame not in self._delayedActions:
			self._delayedActions[frame] = []
		self._delayedActions[frame].append((function,args,kwargs))

	def runDelayedActions(self):
		if self._frame in self._delayedActions:
			actions = self._delayedActions[self._frame]
			for fun, args, kwargs in actions:
				fun(*args, **kwargs)

