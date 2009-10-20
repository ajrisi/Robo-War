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
		self.arena.env.addstr(self.location.y, self.location.x, ".")
	
	
	def go(self):
		while not self.advance(): time.sleep(.05)
	
	
	def advance(self):
		# see if we are already colliding with something
		hadCollision = self.doCollision()
		
		oldX = self.location.x
		oldY = self.location.y
		
		self.location = nextPosition(self.location, self.direction)
		
		# see if we will collide when we advance
		hadCollision = (self.doCollision() or hadCollision)
		
		if hadCollision:
			self.arena.removeBullets([self])
		else:
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
				
				self.arena.env.addstr(0, 0, str(r.health))
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
		self.health = 100
	
	
	def __cmp__(self, other):
		return cmp(self.robotId, other.robotId)
	
	
	def draw(self):
		self.arena.env.addstr(self.location.y, self.location.x, self.displayString())
	
	
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
		time.sleep(.5)
	
	
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
		
		# if no collision (legal move)
		if 0 == self.arena.checkCollision(Point(newX, newY), self):
			self.location.x = newX
			self.location.y = newY
	


class Arena:
	robots = None
	bullets = None
	dimensions = None
	env = None
	
	def __init__(self, xDimension, yDimension, env = None):
		self.robots = []
		self.bullets = []
		self.dimensions = Point(xDimension, yDimension)
		self.env = env
	
	
	def redraw(self):
		self.env.clear()
		self.draw()
		self.env.refresh()
	
	
	def draw(self):
		for r in self.robots:
			r.draw()
		
		for b in self.bullets:
					b.draw()
		
	
	
	
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
			if point.x > self.dimensions.x or point.y > self.dimensions.y or point.x < 0 or point.y < 0:
				# print "robot id %s hit the wall." % robotToTest.robotId
				return 1
		
		return 0


def runGA(env):
	populationLimit = 6
	maxTime = 10
	maxInstructions = 5
	possibleInstructions = ["forward", "reverse", "spin_left", "spin_right", "fire"]
	
	# create the initial population
	population = initPopulation(possibleInstructions, maxInstructions, populationLimit)
	
	# add robots to the arena
	arena = Arena(50, 20, env)
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
		


def initPopulation(possibleInsructions, maxInstructions, populationLimit):
	population = []
	
	r1 = Robot()
	r1.instructions = ["forward", "forward", "forward", "fire", "spin_right"]
	r1.location.x = 10
	r1.location.y = 10
	
	r2 = Robot()
	r2.instructions = ["forward", "forward", "forward", "fire", "spin_left"]
	r2.location.x = 20
	r2.location.y = 10
	
	population = [r1, r2]
	
	# for i in range(populationLimit):
	# 	robot = Robot()
	# 	robot.instructions = [random.choice(possibleInsructions) for i in range(maxInstructions)]
	# 	
	# 	population += [robot]
	
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


def main():
	curses.wrapper(runGA)


if __name__ == '__main__':
	main()
