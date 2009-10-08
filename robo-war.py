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


def runGA(env):
    populationLimit = 6
    maxTime = 10000
	maxInstructions = 5
	possibleInstructions = ["forward", 
							"reverse", 
							"spin_left", 
							"spin_right",
							"fire"]
							
    # create the initial population
    population = initPopulation(possibleInsructions, maxInstructions, populationLimit)

    # when one dies, crossover/mutate, add new to pop, remove old

    for timeSlice in range(1, maxTime):
        # run robots
        # for each killed, crossover/mutate, add new, remove old
		for robot in population:
			runRobot(env, robot)


def initPopulation(possibleInsructions, maxInstructions, populationLimit):
	population = []
	
	for i in range(populationLimit):
		robot = {}
		robot["x"] = 0
		robot["y"] = 0
		robot["direction"] = "up"
		robot["instructions"] = [random.choice(possibleInsructions) for i in range(maxInstructions)]
		
		population += robot
	
	return population


def runRobot(env, robot):
    for instruction in robot["program"]:
        executeInstruction(env, robot, instruction)


def executeInstruction(env, robot, instruction):
    if instruction == "forward":
        if robot["direction"] == "up":
            robot["y"]++
        elif robot["direction"] == "down":
            robot["y"]--
        elif robot["direction"] == "left":
            robot["x"]--
        elif robot["direction"] == "right":
            robot["x"]++
    elif instruction == "reverse":
        if robot["direction"] == "up":
            robot["y"]--
        elif robot["direction"] == "down":
            robot["y"]++
        elif robot["direction"] == "left":
            robot["x"]++
        elif robot["direction"] == "right":
            robot["x"]--
    elif instruction == "spin_left":
        if robot["direction"] == "up":
            robot["direction"] = "left"
        elif robot["direction"] == "left":
            robot["direction"] = "down"
        elif robot["direction"] == "down":
            robot["direction"] = "right"
        elif robot["direction"] == "right":
            robot["direction"] = "up"
    elif instruction == "spin_right":
        if robot["direction"] == "up":
            robot["direction"] = "right"
        elif robot["direction"] == "left":
            robot["direction"] = "up"
        elif robot["direction"] == "down":
            robot["direction"] = "left"
        elif robot["direction"] == "right":
            robot["direction"] = "down"


def drawRobot(env, robot):
	env.addstr(robot["x"], robot["y"], "#")
	env.refresh()

def main():
	curses.wrapper(runGA)

if __name__ == '__main__':
	main()
