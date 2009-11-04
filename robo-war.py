#!/usr/bin/env python
# encoding: utf-8
"""
Adam Risi
Jonathan Potter

Genetic Algorithms, 20091
"""

import sys
import os
import random
import curses
import time


class Point:
	x = None
	y = None
	
	def __init__(self, x = 0, y = 0):
		self.x = x
		self.y = y
	
	
	def __cmp__(self, other):
		xCmp = cmp(self.x, other.x)
		yCmp = cmp(self.y, other.y)
		
		return yCmp if xCmp is 0 else xCmp


class Bullet:
	# static
	staticIdCounter = 0
	
	# instance
	bulletId = None
	location = None
	direction = None
	damage = None
	arena = None
	fromRobot = None
	
	def __init__(self, location = Point(), direction = "up", damage = 1):
		self.bulletId = Bullet.staticIdCounter
		Bullet.staticIdCounter += 1
		
		self.location = location
		self.direction = direction
		self.damage = damage
	
	
	def __cmp__(self, other):
		return cmp(self.bulletId, other.bulletId)
	
	
	def draw(self):
		self.arena.drawString(self.location.x, self.location.y, ".")
	
	
	def go(self):
		while not self.advance():
			if self.arena.env.speed is "slow":
				time.sleep(.03)
			elif self.arena.env.speed is "medium":
				time.sleep(.01)
	
	
	def advance(self):
		# see if we are already colliding with something
		hadCollision = self.doCollision()
		
		# see if we will collide when we advance
		self.location = nextPosition(self.location, self.direction)		
		hadCollision = (self.doCollision() or hadCollision)
		
		if hadCollision:
			self.arena.removeBullets([self])
		
		if self.arena.env.speed is "slow" or self.arena.env.speed is "medium":
			self.arena.redraw()
		
		return hadCollision
	
	
	def doCollision(self):
		# check for wall hit
		if self.location.x > self.arena.dimensions.x:
			return True
		elif self.location.y > self.arena.dimensions.y:
			return True
		elif self.location.x < 0:
			return True
		elif self.location.y < 0:
			return True
		
		# check for robot hit
		for r in self.arena.robots:
			if r.location.x == self.location.x and r.location.y == self.location.y:
				# we hit robot r
				r.health -= self.damage
				r.statistics["hitsTaken"] += 1
				self.fromRobot.statistics["hitsGiven"] += 1
				
				# we killed the robot
				if r.health <= 0:
					self.fromRobot.statistics["kills"] += 1
					self.arena.killRobots([r])
				
				return True
		
		return False
	


class Robot:
	# static
	staticIdCounter = 0
	
	# instance
	location = None
	instructions = None
	direction = None
	health = None
	robotId = None
	arena = None
	statistics = None
	
	def __init__(self):
		self.robotId = Robot.staticIdCounter
		Robot.staticIdCounter += 1
		
		self.location = Point()
		self.instructions = []
		self.direction = "up"
		self.health = 3
		self.statistics = {"lifetime":         0,
						   "shotsFired":       0,
						   "hitsGiven":        0,
						   "hitsTaken":        0,
						   "kills":            0,
						   "distanceTraveled": 0}
	
	
	def __eq__(self, other):
		if not isinstance(other, Robot):
			return False
		
		return self.robotId == other.robotId
	
	def __ne__(self, other):
		return not self.__eq__(other)
	
	def __lt__(self, other):
		if not isinstance(other, Robot):
			return NotImplemented
		
		return self.fitness() < other.fitness()
	
	def __gt__(self, other):
		if not isinstance(other, Robot):
			return NotImplemented
		
		return self.fitness() > other.fitness()
	
	def __le__(self, other):
		if not isinstance(other, Robot):
			return NotImplemented
		
		return self.fitness() <= other.fitness()
	
	def __ge__(self, other):
		if not isinstance(other, Robot):
			return NotImplemented
		
		return self.fitness() <= other.fitness()
	
	
	def fitness(self):
		return self.statistics["lifetime"]
	
	
	def draw(self):
		redLevel = 1
		yellowLevel = 2
		greenLevel = 3
		
		if self.health <= redLevel:
			color = Arena.COLOR_PAIR_RED
		elif self.health <= yellowLevel:
			color = Arena.COLOR_PAIR_YELLOW
		elif self.health <= greenLevel:
			color = Arena.COLOR_PAIR_GREEN
		else:
			color = 0
		
		self.arena.drawString(self.location.x, self.location.y, self.displayString(), color)
	
	
	def runInstructions(self):
		for x in self.instructions:
			self.runInstruction(x)
	
	def runInstruction_n(self, n):
		self.runInstruction(self.instructions[n])
	
	def runInstruction(self, x):
		action = {  "forward":    self.moveForward, 
					"reverse":    self.moveReverse, 
					"spin_left":  self.spinLeft, 
					"spin_right": self.spinRight,
					"fire":       self.fire }
		
		action[x]()
	
	
	def displayString(self):
		if self.direction == "up":
			display = "^"
		elif self.direction == "down":
			display = "v"
		elif self.direction == "left":
			display = "<"
		else: # right
			display = ">"
		
		return display
	
	
	def fire(self):
		self.statistics["shotsFired"] += 1
		
		bulletDirection = self.direction
		bulletLocation = nextPosition(self.location, bulletDirection)
		
		bullet = Bullet(bulletLocation, bulletDirection)
		bullet.fromRobot = self
		self.arena.fire(bullet)
	
	
	def spinLeft(self):
		self.spin(-1)
	
	
	def spinRight(self):
		self.spin(1)
	
	
	# direction should be 1/-1 for right/left respectively
	def spin(self, direction):
		d = ["up", "right", "down", "left"]
		currentIndex = d.index(self.direction)
		newIndex = (currentIndex + (1*direction)) % len(d)
		self.direction = d[newIndex]
	
	
	def moveForward(self):
		self.move(1)
	
	
	def moveReverse(self):
		self.move(-1)
	
	
	# direction should be -1/1 for reverse/forward respectively
	def move(self, direction):
		self.statistics["distanceTraveled"] += 1
		
		deltaX = 0
		deltaY = 0
		
		if self.direction == "up":
			deltaY += (-1 * direction)
		elif self.direction == "down":
			deltaY += (1 * direction)
		elif self.direction == "left":
			deltaX += (-1 * direction)
		elif self.direction == "right":
			deltaX += (1 * direction)
		
		newX = self.location.x + deltaX
		newY = self.location.y + deltaY
		
		newY = (newY + self.arena.dimensions.y) % self.arena.dimensions.y
		newX = (newX + self.arena.dimensions.x) % self.arena.dimensions.x
		
		# if no collision (legal move)
		if 0 == self.arena.checkCollision(Point(newX, newY), self):
			self.location.x = newX
			self.location.y = newY
	


class Arena:
	# static
	COLOR_PAIR_RED = 1
	COLOR_PAIR_YELLOW = 2
	COLOR_PAIR_GREEN = 3
	
	# instance
	robots = None
	bestDeadRobots = None
	bullets = None
	dimensions = None
	upperLeft = None
	env = None
	
	def __init__(self, env):
		# instance
		self.robots = []
		self.bestDeadRobots = []
		self.bullets = []
		self.env = env
		self.upperLeft = Point(0, 0)
		self.resize()
	
	
	def resize(self):
		(y, x) = self.env.screen.getmaxyx()
		self.dimensions = Point(x, y)
	
	
	def redraw(self):
		self.env.screen.clear()
		self.draw()
		self.env.screen.refresh()
	
	
	def draw(self):
		for r in self.robots:
			r.draw()
		
		for b in self.bullets:
			b.draw()
	
	
	def drawString(self, x, y, s, color = 0):
		try:
			self.env.screen.addstr(self.upperLeft.y + y, self.upperLeft.x + x, s, curses.color_pair(color))
		except:
			pass
	
	
	def fire(self, bullet):
		self.addBullets([bullet])
		bullet.go()
	
	
	def addBullets(self, bullets):
		for b in bullets:
			# don't add duplicates
			try:
				self.bullets.index(b)
			except:
				b.arena = self
				self.bullets += [b]
	
	
	def removeBullets(self, bullets):
		for b in bullets:
			self.bullets.remove(b)
	
	
	def killRobots(self, robots):
		# remove the dead robots
		self.removeRobots(robots)
		
		# add robot to dead array if they aren't already there
		for r in robots:
			if r not in self.bestDeadRobots:
				self.bestDeadRobots += [r]
		
		# truncate the best dead robots to only keep the very best
		self.bestDeadRobots.sort(reverse=True)
		self.bestDeadRobots = self.bestDeadRobots[:self.env.numberOfDeadToKeep]
		
		# crossover and mutate to produce new individuals to replace robots
		newRobots = crossoverMutate(self, robots)
		
		# add the new robots to the arena
		self.addRobots(newRobots)
	
	
	def addRobots(self, robots):
		for r in robots:
			# don't add duplicates
			try:
				self.robots.index(r)
			except:
				r.arena = self
				self.robots += [r]
	
	
	def removeRobots(self, robots):
		for r in robots:
			self.robots.remove(r)
	
	
	def checkCollision(self, point, robotToTest):
		for r in self.robots:
			if robotToTest.robotId != r.robotId and point.x == r.location.x and point.y == r.location.y:
				# print "robot id %s collided with robot id %s. Locations (%s, %s) (%s, %s)" % (robotToTest.robotId, r.robotId, robotToTest.location.x, robotToTest.location.y, r.location.x, r.location.y)
				return 1
		
		return 0
	


class Environment:
	
	# instance
	speed = None
	mutationRate = None
	amountToSelect = None
	populationLimit = None
	stoppingCondition = None
	convergence = None
	maxTime = None
	numberOfDeadToKeep = None
	
	screen = None
	
	possibleInstructions = None
	maxInstructions = None
	
	shouldPlot = None
	shouldLog = None
	
	def __init__(self, screen):
		# instance
		self.speed = "fast"
		self.mutationRate = .25
		self.amountToSelect = 10
		self.populationLimit = 10
		self.stoppingCondition = "time"
		self.convergence = {"timeChange": 500, "valueChange": 1}
		self.maxTime = 2000
		self.numberOfDeadToKeep = 10
		
		self.screen = screen
		
		self.possibleInstructions = ["forward", "reverse", "spin_left", "spin_right", "fire"]
		self.maxInstructions = 50
		
		self.shouldPlot = False
		self.shouldLog = False
	


def runGA(env):
	logs = initLogs(env)
	plot = initPlot(env)
	
	# initialize arena and generation zero
	arena = Arena(env)
	population = initPopulation(arena)
	arena.addRobots(population)
	
	# draw all of our robots to start with
	if env.speed is not "fastest":
		arena.redraw()
	
	# for convergence detection
	bestFitnesses = []
	hasConvergence = False
	
	for timeSlice in range(1, env.maxTime):
		# run robots
		for i in range(0, env.maxInstructions):
			for robot in arena.robots:
				robot.runInstruction_n(i)
			
			# draw the arena each frame unless we are going very fast
			if env.speed is not "fastest":
				arena.redraw()
			
			# sleep based on env.speed
			if env.speed is "slow":
				time.sleep(.3)
			elif env.speed is "medium":
				time.sleep(.08)
			
		for r in arena.robots:
			r.statistics["lifetime"] += 1
		
		# get all of the robots, living and dead and sort them best first
		allRobots = arena.robots + arena.bestDeadRobots
		allRobots.sort(reverse=True)
		
		logSlice(env, logs, timeSlice, arena.robots, arena.bestDeadRobots)
		plotSlice(env, plot, timeSlice, arena.robots, arena.bestDeadRobots)
		
		# check for convergence
		if env.stoppingCondition is "convergence":
			if len(allRobots) > 0:
				bestFitnesses += [allRobots[0].fitness()]
		
			if len(bestFitnesses) >= 2:
				mostRecent = bestFitnesses[-1]
				for i in range(len(bestFitnesses)):
					if bestFitnesses[i] + env.convergence["valueChange"] > mostRecent:
						if len(bestFitnesses) - i >= env.convergence["timeChange"]:
							hasConvergence = True
						break
		
			if hasConvergence:
				break
		
	
		
	closeLogs(env, logs)
	closePlot(env, plot)


def initPopulation(arena):
	population = []
	env = arena.env
	
	for i in range(env.populationLimit):
		robot = Robot()
	 	robot.instructions = [random.choice(env.possibleInstructions) for i in range(env.maxInstructions)]
		robot.location.x = random.randrange(0, arena.dimensions.x)
		robot.location.y = random.randrange(0, arena.dimensions.y)
	 	
	 	population += [robot]
	
	return population


def nextPosition(location, direction, amount = 1):
	newLocation = Point(location.x, location.y)
	
	if direction == "up" or direction == "down":
		if direction == "up": delta = -1 * amount
		else:                 delta = amount
		
		newLocation.y += delta
	
	
	elif direction == "left" or direction == "right":
		if direction == "left": delta = -1 * amount
		else:                   delta = amount
		
		newLocation.x += delta
	
	return newLocation


def initCurses():
	curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
	curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
	
	try:
		curses.curs_set(0)
	except:
		pass


def initLogs(env):
	if not env.shouldLog:
		return
	
	verboseFile = open("verbose_statistics", "w")
	
	return verboseFile


def initPlot(env):
	if not env.shouldPlot:
		return
	
	# initialize stats file	
	statfile = open("stats", "w");
	statfile.write("0 0 0 0 0\n")
	statfile.flush()
	
	gnuplot = os.popen("gnuplot -persist", "w")
	
	# initialize gnuplot
	gnuplot.write("set terminal x11\n")
	gnuplot.write("set title \"Generation vs Fitness\"\n")
	gnuplot.write("plot 'stats' using 1:2 title 'Overall Best' with lines, 'stats' using 1:3 title 'Best' with lines, 'stats' using 1:4 title 'Average' with lines, 'stats' using 1:5 title 'Worst' with lines\n")
	
	return (statfile, gnuplot)


def logSlice(env, logs, timeSlice, aliveRobots, deadRobots):
	if not env.shouldLog:
		return
	
	verboseFile = logs
	allRobots = aliveRobots + deadRobots
	allRobots.sort(reverse=True)
	
	if len(allRobots) > 0:
		verboseFile.write("time         : " + str(timeSlice) + "\nstatistics   : " + str(allRobots[0].statistics) + "\ninstructions : " + str(allRobots[0].instructions) + "\n\n")
		verboseFile.flush()
	

	
def plotSlice(env, plot, timeSlice, aliveRobots, deadRobots):
	if not env.shouldPlot:
		return
	
	(statFile, gnuplot) = plot
	allRobots = aliveRobots + deadRobots
	allRobots.sort(reverse=True)
	aliveRobots.sort(reverse=True)
	
	if len(allRobots) > 0 and len(aliveRobots) > 0:
		overallBest = allRobots[0].fitness()
		best = aliveRobots[0].fitness()
		average = float(sum(x.fitness() for x in aliveRobots)) / float(len(aliveRobots))
		worst = aliveRobots[-1].fitness()
		
		statFile.write(str(timeSlice) + " " + str(overallBest) + " " + str(best) + " " + str(average) + " " + str(worst) + "\n")
		statFile.flush()
		
		gnuplot.write("replot\n")
		try:
			gnuplot.flush()
		except:
			pass
	


def closeLogs(env, logs):
	if not env.shouldLog:
		return
	
	verboseFile = logs
	
	verboseFile.close()


def closePlot(env, plot):
	if not env.shouldPlot:
		return
	
	(statFile, gnuplot) = plot
	
	statFile.close()
	gnuplot.close()


def crossoverMutate(arena, robotsToReplace):
	env = arena.env
	newRobots = []
	
	allRobots = arena.robots + arena.bestDeadRobots
	allRobots.sort(reverse=True)
	
	selected = allRobots[:env.amountToSelect]
	
	for oldRobot in robotsToReplace:
		newRobot = crossover(env, random.choice(selected), random.choice(selected))
		newRobot.location.x = oldRobot.location.x
		newRobot.location.y = oldRobot.location.y
		
		if random.uniform(0, 1) <= env.mutationRate:
			mutate(env, newRobot)
		
		newRobots += [newRobot]
	
	return newRobots


def crossover(env, robota, robotb):
	#crossover the robots instruction arrays at their midpoint
	lena = len(robota.instructions)
	lenb = len(robotb.instructions)
	newinstr = robota.instructions[:lena/2]
	newinstr += robotb.instructions[lenb/2:]
	
	newrobo = Robot()
	newrobo.instructions = newinstr
	newrobo.location.x = 0
	newrobo.location.y = 0
	
	return newrobo


def mutate(env, robota):
	# randomly replace one instruction with another
	newrobo = Robot()
	newrobo.instructions = robota.instructions
	newrobo.instructions[random.randrange(0, len(newrobo.instructions))] = random.choice(env.possibleInstructions)
	
	newrobo.location = robota.location
	
	
	return newrobo


def cursesMain(screen):
	# initialize curses
	initCurses()
	
	# initialize environment
	env = Environment(screen)
	
	env.speed 					= "fastest"
	env.mutationRate 			= .25
	env.amountToSelect 			= 10
	env.populationLimit 		= 10
	env.stoppingCondition 		= "convergence"
	env.convergence				= {"timeChange": 500, "valueChange": 1}
	env.maxTime 				= 2000
	env.numberOfDeadToKeep 		= 10
	
	env.possibleInstructions 	= ["forward", "reverse", "spin_left", "spin_right", "fire"]
	env.maxInstructions 		= 50
	
	env.shouldPlot 				= False
	env.shouldLog 				= False
	
	runGA(env)
	


def main():
	curses.wrapper(cursesMain)


if __name__ == '__main__':
	main()
