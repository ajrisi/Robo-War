#!/usr/bin/env python
# encoding: utf-8
"""
Created by Jonathan Potter on 2009-10-03.
Copyright (c) 2009 Jonathan Potter. All rights reserved.
"""

import sys
import os
import random

def runGA():
	populationLimit = 10
	generations = 10
	
	# Initialize our population
	population = initializePopulation(populationLimit)
	
	printGeneration(0, population)
	
	for generationNumber in range(1, generations + 1):
		offspring = selectionCrossoverMutation(population)
		
		population = insertIntoPopulation(offspring, population, populationLimit)
		
		printGeneration(generationNumber, population)


def printGeneration(generationNumber, population):
	print " - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
	print "Generation Number: %s" % generationNumber
	print "Max / Min Fitness: %s / %s" % (fitness(population[0]), fitness(population[-1]))
	print "Population:"
	
	for x in population:
		print "\tID: %s" % id(x)
		print "\tFeature Vector: %s" % x
		print "\tFitness: %s\n" % fitness(x)
	
	print " - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
	


def initializePopulation(populationLimit):
	return [[(random.random() * (10 ** 5) % 10) - 5, (random.random() * (10 ** 5) % 10) - 5] for x in range(populationLimit)]


def selectionCrossoverMutation(population):
	offspring = []
	
	for i in range(len(population)/2):
		x = random.choice(population)
		y = random.choice(population)
		
		# mutation(random.choice(population))
		
		offspring += [crossover(x,y)]
	
	return offspring


def crossover(x, y):
	if len(x) != len(y):
		return []
		
	if len(x) < 2:
		return []
	
	return [x[0], y[1]]


def mutation(x):
	if len(x) < 2:
		return []
	
	r = ((random.random() * (10 ** 5)) % 3)
	delta = ((random.random() * (10 ** 5)) % 2) - 1
	
	if r == 0:
		x[0] += delta
	elif r == 1:
		x[1] += delta
	else:
		x[0] += delta
		x[1] += delta
	
	x = fixIndividual(x)
	
	return x


def insertIntoPopulation(offspring, population, populationLimit):
	population += offspring
	
	population.sort(cmp=fitnessCompare,reverse=True)
	
	population = population[:populationLimit]
	
	return population


# Compare two element's fitness (for sorting our population)
def fitnessCompare(x,y):
	fX = fitness(x)
	fY = fitness(y)
	
	if   fX > fY:  return 1
	elif fX == fY: return 0
	else:          return -1


def genotypeToPhenotype(genotype):
	# There is a direct mapping from our genotype to phenotype.
	# The genotype and phenotype are the same because they are each so simple (just two numbers).
	return genotype


# Clamp the values for a child in the range [-5,5]
def fixIndividual(x):
	for i in range(len(x)):
		if x[i] > 5: x[i] = 5
		elif x[i] < -5: x[i] = -5
	
	return x


def fitness(x):
	# This shouldn't happen, but if a genotype doesn't have two values it's broken
	if len(x) < 2: return -10
	
	# Evaluate the function
	return x[0] ** 2 + x[1] ** 2


def main():
	runGA()


if __name__ == '__main__':
	main()

