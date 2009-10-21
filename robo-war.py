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
		while not self.advance(): time.sleep(.01)
	
	
	def advance(self):
		# see if we are already colliding with something
		hadCollision = self.doCollision()
		
		# see if we will collide when we advance
		self.location = nextPosition(self.location, self.direction)		
		hadCollision = (self.doCollision() or hadCollision)
		
		if hadCollision:
			self.arena.removeBullets([self])
		
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
				
				# we killed the robot
				if r.health <= 0:
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
	
	def __init__(self):
		self.robotId = Robot.staticIdCounter
		Robot.staticIdCounter += 1
		
		self.location = Point()
		self.instructions = []
		self.direction = "up"
		self.health = 3
	
	
	def __cmp__(self, other):
		return cmp(self.robotId, other.robotId)
	
	
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
	
	
	def runInstruction(self, x):
		action = {  "forward":    self.moveForward, 
					"reverse":    self.moveReverse, 
					"spin_left":  self.spinLeft, 
					"spin_right": self.spinRight,
					"fire":       self.fire }
		
		action[x]()
		self.arena.redraw()
		time.sleep(.05)
	
	
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
		bulletDirection = self.direction
		bulletLocation = nextPosition(self.location, bulletDirection)
		
		bullet = Bullet(bulletLocation, bulletDirection)
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

		newY = newY + self.arena.dimensions.y % self.arena.dimensions.y
		newX = newX + self.arena.dimensions.x % self.arena.dimensions.x
		
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
	bullets = None
	dimensions = None
	upperLeft = None
	env = None
	
	def __init__(self, env):
		# instance
		self.robots = []
		self.bullets = []
		self.env = env
		self.upperLeft = Point(0, 0)
		self.resize()
	
	
	def resize(self):
		(y, x) = self.env.getmaxyx()
		self.dimensions = Point(x, y)
	
	
	def redraw(self):
		self.env.clear()
		self.draw()
		self.env.refresh()
	
	
	def draw(self):
		for r in self.robots:
			r.draw()
		
		for b in self.bullets:
					b.draw()
		
	
	def drawString(self, x, y, s, color = 0):
		try:
			self.env.addstr(self.upperLeft.y + y, self.upperLeft.x + x, s, curses.color_pair(color))
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
		# TODO: crossover / mutate, add new robots
		
		# remove the dead robots
		self.removeRobots(robots)
	
	
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


def runGA(env):
	# initialize curses colors
	initColors()
	
	populationLimit = 6
	maxTime = 20
	maxInstructions = 5
	possibleInstructions = ["forward", "reverse", "spin_left", "spin_right", "fire"]

	# create the arena 
	arena = Arena(env)
	
	# create the initial population
	population = initPopulation(arena, possibleInstructions, maxInstructions, populationLimit)
	
	#add robots to the arena
	arena.addRobots(population)
	
	# when one dies, crossover/mutate, add new to pop, remove old
	
	# draw all of our robots to start with
	for robot in arena.robots:
		robot.draw()
	
	for timeSlice in range(1, maxTime):
		# run robots
		for robot in arena.robots:
			robot.runInstructions()
		
		# for each killed, crossover/mutate, add new, remove old
		


def initPopulation(arena, possibleInsructions, maxInstructions, populationLimit):
	population = []

	for i in range(populationLimit):
		robot = Robot()
	 	robot.instructions = [random.choice(possibleInsructions) for i in range(maxInstructions)]
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


def initColors():
	curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
	curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

def crossover(robota, robotb):
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

def mutate(robota):
	# randomly replace one instruction with another
	newrobo = Robot()
	newrobo.instructions = robota.instructions
	newrobo.instructions[random.randrange(0, len(newrobo.instructions))] = random.choice(possibleInstructions)

	newrobo.location.x = 0
	newrobo.location.y = 0

	return newrobo

def main():
	curses.wrapper(runGA)


if __name__ == '__main__':
	main()
