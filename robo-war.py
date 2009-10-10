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


class Arena:
	robots = None
	dimensions = None
	
	def __init__(self, xDimension, yDimension):
		self.robots = []
		self.dimensions = Point(xDimension, yDimension)
	
	def addRobots(self, robots):
		for r in robots:
			# don't add duplicates
			if self.indexOfRobot(r) < 0:
				r.arena = self
				self.robots += [r]
	
	def fire(self, location, direction, env):
		pass
			
	def indexOfRobot(self, robot):
		for i in range(len(self.robots)):
			if self.robots[i].robotId == robot.robotId:
				return i
		
		return -1
	
	def checkCollision(self, point, robotToTest):
		for r in self.robots:
			if robotToTest.robotId != r.robotId and point.x == r.location.x and point.y == r.location.y:
				# print "robot id %s collided with robot id %s. Locations (%s, %s) (%s, %s)" % (robotToTest.robotId, r.robotId, robotToTest.location.x, robotToTest.location.y, r.location.x, r.location.y)
				return 1
			if point.x > self.dimensions.x or point.y > self.dimensions.y or point.x < 0 or point.y < 0:
				# print "robot id %s hit the wall." % robotToTest.robotId
				return 1
		
		return 0



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
	
	
	def draw(self, env):
		env.addstr(self.location.y, self.location.x, self.displayString())
		env.refresh()
	
	def runInstructions(self, env):
		for x in self.instructions:
			self.runInstruction(x, env)
	
	def runInstruction(self, x, env):
		action = {  "forward":    self.moveForward, 
					"reverse":    self.moveReverse, 
					"spin_left":  self.spinLeft, 
					"spin_right": self.spinRight,
					"fire":       self.fire }
		
		action[x](env)
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


	def fire(self, env):
		self.arena.fire(self.location, self.direction, env)
	

	def spinLeft(self, env):
		self.spin(-1, env)


	def spinRight(self, env):
		self.spin(1, env)


	# direction should be 1/-1 for right/left respectively
	def spin(self, direction, env):
		d = ["up", "right", "down", "left"]
		currentIndex = d.index(self.direction)
		newIndex = (currentIndex + (1*direction)) % len(d)
		self.direction = d[newIndex]
		
		env.addstr(self.location.y, self.location.x, " ")
		env.addstr(self.location.y, self.location.x, self.displayString())
		env.refresh()


	def moveForward(self, env):
		self.move(1, env)


	def moveReverse(self, env):
		self.move(-1, env)
	
	
	# direction should be -1/1 for reverse/forward respectively
	def move(self, direction, env):
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
			env.addstr(self.location.y, self.location.x, " ")
			env.addstr(newY, newX, self.displayString())
			env.refresh()
	
			self.location.x = newX
			self.location.y = newY



def runGA(env):
	populationLimit = 6
	maxTime = 10
	maxInstructions = 5
	possibleInstructions = ["forward", "reverse", "spin_left", "spin_right", "fire"]
							
	# create the initial population
	population = initPopulation(possibleInstructions, maxInstructions, populationLimit)
	
	# add robots to the arena
	arena = Arena(100, 100)
	arena.addRobots(population)
	
	# when one dies, crossover/mutate, add new to pop, remove old
	
	# draw all of our robots to start with
	for robot in arena.robots:
		robot.draw(env)
	
	for timeSlice in range(1, maxTime):
		# run robots
		for robot in arena.robots:
			robot.runInstructions(env)
		
		# for each killed, crossover/mutate, add new, remove old
		


def initPopulation(possibleInsructions, maxInstructions, populationLimit):
	population = []
	
	r1 = Robot()
	r1.instructions = ["forward", "forward", "forward", "forward", "spin_right"]
	r1.location.x = 10
	r1.location.y = 10
	
	r2 = Robot()
	r2.instructions = ["forward", "forward", "forward", "forward", "spin_left"]
	r2.location.x = 20
	r2.location.y = 20
	
	population = [r1, r2]
	
	# for i in range(populationLimit):
	# 	robot = Robot()
	# 	robot.instructions = [random.choice(possibleInsructions) for i in range(maxInstructions)]
	# 	
	# 	population += [robot]
	
	return population



def main():
	curses.wrapper(runGA)

if __name__ == '__main__':
	main()
