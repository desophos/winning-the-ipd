'''
Created on Mar 8, 2013
'''

from globals import NUM_INDIVIDUALS, NUM_INITIAL_STATES, DEFAULT_MEMORY


class Environment:
    def generate_population(self, num_states=NUM_INITIAL_STATES, memory=DEFAULT_MEMORY):
        population = []
        for _ in range(NUM_INDIVIDUALS):
            population.append(self.individual(num_states=num_states, memory=memory))
        return population
