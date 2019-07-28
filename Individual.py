'''
Created on Mar 10, 2013
'''

from globals import NUM_INITIAL_STATES, DEFAULT_MEMORY, ACTION_PROB_STEP_NUM, ACTION_PROB_LEN
from random import choice
from utility import list_to_number, weighted_choice


class Individual:
    __slots__ = ['chromosome', 'num_states', 'bcd_length', 'state_instruction_length']

    def __init__(self, chromosome=None, num_states=NUM_INITIAL_STATES, memory=DEFAULT_MEMORY):
        self.move_history = []  # we use this to keep track of all our previous moves
        if num_states:
            self.num_states = num_states
        if memory:
            self.memory = memory

        self.recalculate_attributes()

        if chromosome:
            self.chromosome = chromosome
        else:
            self.chromosome = self.generate_chromosome()

    def recalculate_attributes(self):
        self.bcd_length = len(bin(self.num_states-1)[2:])

    def generate_chromosome(self):
        # game-specific individuals must implement this
        raise NotImplementedError

    def generate_random_state(self):
        # generate a BCD state
        dec_state = choice(range(self.num_states))  # pick a random state
        state_BCD = bin(dec_state)[2:].zfill(self.bcd_length)  # a BCD left-filled with zeros up to self.bcd_length
        state = []
        for c in state_BCD:  # for each character in the BCD string
            state.append(int(c))  # append it as an int to the state list
        return state

    def generate_random_prob(self):
        bin_max_prob = bin(ACTION_PROB_STEP_NUM)[2:]
        dec_chosen_prob = choice(range(ACTION_PROB_STEP_NUM+1))
        bin_chosen_prob = bin(dec_chosen_prob)[2:].zfill(len(bin_max_prob))
        prob = []
        for c in bin_chosen_prob:
            prob.append(int(c))
        return prob

    def find_current_position(self, state):
        # game-specific individuals must implement this
        raise NotImplementedError

    def calculate_cooperation_probability(self, state):
        current_pos = self.find_current_position(state)
        if current_pos == (current_pos + ACTION_PROB_LEN - 1):
            return list_to_number([self.chromosome[current_pos]]) / float(ACTION_PROB_STEP_NUM)
        else:
            return list_to_number(self.chromosome[current_pos : current_pos+ACTION_PROB_LEN-1]) / float(ACTION_PROB_STEP_NUM)

    def find_move(self, state):
        # the state can be higher than the max state because
        # there are a certain number of binary digits in each state.
        # those digits are randomly generated, so we can end up with
        # a state higher than we actually have.
        # so, constrain the state to the maximum state we actually have.
        # this is a terrible solution, but it'll do for now, i suppose.
        if state >= self.num_states:
            state = self.num_states-1
        """
        print "finding move"
        print 'num states', self.num_states
        print 'bcd length', self.bcd_length
        print 'state instruction length', self.state_instruction_length
        print 'player len', len(self.chromosome)
        print 'player', self.chromosome
        print 'state', state
        print 'current_pos', self.find_current_position(state)
        """
        coop_prob = self.calculate_cooperation_probability(state)
        return weighted_choice([coop_prob, 1-coop_prob])

    def split_into_states(self):
        """Split a player into its constituent states."""
        for i in xrange(0, len(self.chromosome), self.STATE_LENGTH):
            yield self.chromosome[i:i+self.STATE_LENGTH]
