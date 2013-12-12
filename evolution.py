'''
Created on Mar 3, 2013

@author: Daniel Horowitz
'''
from random import shuffle
from itertools import islice
from matplotlib import pyplot
from collections import deque

def evolution(populations, fn, individual_type, gen, args):
    # This function provides genetic algorithm functionality for multiple populations.
    
    # populations is a list of the starting populations, preferably randomly generated.
    # fn is the fitness function.
    # gen is the number of generations to run.
    # args is a dict of command line arguments, the contents of which are apparent below.

    fitness_fn = fn
    genes=[0,1]
    max_population = len(populations[0])
    
    num_generations=gen
    num_populations=args['populations_num']
    pruning_num=args['pruning_num']
    mutation_probability=args['mutation_probability']
    structure_mutation_probability=args['structure_mutation_probability']
    num_gene_mutations=args['mutations_num']
    
    fitness_tracker = []
    
    for i in range(num_populations):
        fitness_tracker.append([])
    
    generation = 0
    
    # we just need one permutation for each population,
    # because it doesn't matter what order the other ones are in
    # so we'll rotate a deque each time through
    populations = deque(populations)
    
    while generation < num_generations:
        # compare each population against the other populations
        for i in range(len(populations)):
            populations[0], fitness_list = reproduce(populations, max_population, fitness_fn, individual_type, genes, num_generations, pruning_num, mutation_probability, structure_mutation_probability, num_gene_mutations)
            fitness_tracker[i].append(fitness_list)
            populations.rotate(1) # so we work with the next population next time
        # now the populations have been fully rotated
        print generation+1
        generation += 1
    
    top_fitness_lists = []
    for i in range(num_populations):
        top_fitness_lists.append([])
    
    for i in range(num_populations):
        for fitness_list in fitness_tracker[i]:
            top_fitness_lists[i].append(fitness_list[0]) # append the fitness of the top individual in each population
        pyplot.plot(top_fitness_lists[i])
        
    legend_strs = []
    for i in range(num_populations):
        legend_strs.append("Population "+str(i+1))
    
    pyplot.xlabel("Generation")
    pyplot.ylabel("Average fitness")
    pyplot.legend( tuple(legend_strs), loc="best" )
    
    pyplot.show()
    
    return populations
    
def reproduce(populations, max_population, fitness_fn, individual_type, genes, num_generations, pruning_num, mutation_probability, structure_mutation_probability, num_mutations):
    # 1. Remove the PRUNING_NUM worst-performing individuals from the population.
    # 2. Allow the remaining (max_population - PRUNING_NUM) individuals directly into the next generation.
    # 3. Replace the removed individuals with individuals created by mating individuals from the previous generation.
    
    old_population = populations[0] 
    
    fitness_list = calculate_fitness(populations, fitness_fn)
    new_population, fitness_list = trim_population(populations[0], fitness_list, pruning_num)
    
    while len(new_population) < max_population: # maintain the number of individuals in the population
        x = random_selection(old_population, fitness_list)
        y = random_selection(old_population, fitness_list)
            
        crossed, states = crossover(x,y)
        child = individual_type(crossed, states) # x.num_states should be same as y.num_states
        """
        print 'x num states', x.num_states
        print 'x bcd length', x.bcd_length
        print 'x state instruction length', x.state_instruction_length
        print 'x len', len(x.chromosome)
        
        print 'x', x.chromosome
        
        print 'y num states', y.num_states
        print 'y bcd length', y.bcd_length
        print 'y state instruction length', y.state_instruction_length
        print 'y len', len(y.chromosome)
        
        print 'y', y.chromosome
        
        print 'num states', child.num_states
        print 'bcd length', child.bcd_length
        print 'state instruction length', child.state_instruction_length
        print 'child len', len(child.chromosome)
        
        print 'child', child.chromosome
        """
        
        #if random() <= mutation_probability: # if this is here, mutation_probability is the probability of any mutations at all -- do we want this?
        mutate(child, genes, mutation_probability, structure_mutation_probability, num_mutations)
        new_population.append(child)
    return new_population, fitness_list

def crossover(x,y):
    # This function simulates crossover.
    from random import randint
    
    xlen = len(x.chromosome)
    ylen = len(y.chromosome)

    # take the length of the shorter chromosome
    if xlen <= ylen:
        shorter = x
        longer = y
    else:
        shorter = y
        longer = x
        
    crossover_point = randint(1,len(shorter.chromosome)-1) # find a random crossover point not at the ends of the shorter chromosome
    
    # return the crossed-over chromosome and its num_states
    return shorter.chromosome[0 : crossover_point] + longer.chromosome[crossover_point : len(longer.chromosome)], \
        longer.num_states
    
def mutate(individual, genes, mutation_probability, structure_mutation_probability, num_mutations):
    # This function simulates mutation.
    from random import random, sample, choice
    
    # mutate num_mutations random genes, each at mutation_probability probability
    locations_to_modify = sample(range(len(individual.chromosome)), num_mutations)
    for location in locations_to_modify:        
        if random() <= mutation_probability: # if this is here, mutation_probability is the probability of each mutation -- do we want this?
            individual.chromosome[location] = choice(genes) # randomly changes the gene at the location based on the given range of values
    #if random() <= structure_mutation_probability:
    #    individual.mutate_structure()
    
def calculate_fitness(populations, fitness_fn):
    """
    We have a number of possibilities for fitness calculation here.
    We could match each individual against a randomly selected individual from the other population,
    we could average each individual's fitness against all members of the other population,
    or other possibilities I haven't thought of.
    For now, I'll average the fitness against all members of the other population.
    """
    
    # calculate fitness of each individual in population
    fitness_list = []
    
    if len(populations) == 1:
        for individual in populations[0]:
            fitness = fitness_fn(individual) # get reward
            fitness_list.append(fitness)

    if len(populations) >= 2:
        for individual in populations[0]:
            for population in islice(populations, 1, None): # islice because populations is a deque
                shuffle(population) # randomize order so we have random players from the other populations
                # this is lazy because it selects with replacement
            fitness_sum = 0
            # for opponent group in opponent populations
            for opponents in zip(*islice(populations, 1, None)): # islice because populations is a deque
                fitness_sum += fitness_fn(individual, opponents) # get reward
            fitness_avg = fitness_sum / len(populations[0]) # every population is the same length
            fitness_list.append(fitness_avg)

    return fitness_list

def trim_population(population, fitness_list, pruning_num):
    # This function returns a list of pruning_num most fit individuals from the population.
    
    
    sorted_population, sorted_fitness_list = zip( *sorted( zip(population, fitness_list), key=lambda i:i[1], reverse=True ) )
    # Let's take a break to parse this line out.
    # zip(population, fitness_list) zips the two lists together so that each individual is associated with its fitness.
    # sorted(zip(etc.), key=lambda i: i[1], reverse=True) sorts the zipped list of tuples by each second parameter (i.e. the fitness) from greatest to smallest.
    # zip(*sorted(etc.)) unzips the list of tuples back into two n-tuples.
    # zip(*sorted(etc.))[0] gets the first tuple, i.e. the population sorted from greatest to smallest fitness!
    # Now it's time to move on :)
    
    # convert them to lists
    sorted_population = list(sorted_population)
    sorted_fitness_list = list(sorted_fitness_list)
    
    # find the pruning_num most fit individuals
    num_to_keep = len(population) - pruning_num
    if pruning_num > 0:
        trimmed_population = sorted_population[0:num_to_keep]
        sorted_fitness_list = sorted_fitness_list[0:num_to_keep]
    else:
        trimmed_population = sorted_population
    
    return trimmed_population, sorted_fitness_list

def random_selection(population, fitness_list):
    # randomly select an individual from the trimmed population weighted by fitness
    # uses the subtraction algorithm from 
    # http://eli.thegreenplace.net/2010/01/22/weighted-random-generation-in-python/
    
    from random import random
    
    rnd = random() * sum(fitness_list)
    for i, w in enumerate(fitness_list):
        rnd -= w
        if rnd < 0:
            return population[i]