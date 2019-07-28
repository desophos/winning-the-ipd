'''
Created on Mar 10, 2013
'''

from Individual import Individual
from utility import list_to_number
from globals import ACTION_PROB_LEN, ACTION_PROB_STEP_NUM, NUM_INITIAL_STATES, DEFAULT_MEMORY


class RPD_Individual(Individual):
    __slots__ = []

    def __init__(self, chromosome=None, num_states=NUM_INITIAL_STATES, memory=DEFAULT_MEMORY):
        Individual.__init__(self, chromosome, num_states)

    def recalculate_attributes(self):
        Individual.recalculate_attributes(self)
        self.state_instruction_length = ACTION_PROB_LEN + self.bcd_length * 2**self.memory

    def generate_chromosome(self):
        # This function generates the chromosome of a finite state automaton such that:
        # 1. each state identifier is represented by a binary coded decimal (BCD)
        # 2. the initial state is represented by a BCD at the beginning of the chromosome
        # 3. each state has the following structure:
        #    #... #... #...
        #    the first set of digits is the probability to cooperate when in internal state i.
        #    the first set of digits is a BCD representing the state to transition to if the opponent is observed to cooperate.
        #    the second set of digits is a BCD representing the state to transition to if the opponent is observed to defect.
        # 4. the chromosome is composed of num_states representations as described in (3).
        # 5. num_states also determines the number of transition states and thus the BCD limit for each transition state encoding.
        # 6. each digit is in {0,1}.
        #from random import choice

        #genes = [0,1]

        chromosome = []

        # add the initial state
        chromosome.extend(self.generate_random_state())

        for _ in range(self.num_states):
            # each state consists of the probability to cooperate (as a BCD) and two BCDs.
            chromosome.extend(self.generate_random_prob())
            for _ in range(2**self.memory): # generate enough states to represent all our possible state changes
                chromosome.extend(self.generate_random_state())

        return chromosome

    def mutate_structure(self):
        """ change my number of states """
        from random import choice
        from math import log

        print 'mutating structure'
        print 'num states', self.num_states
        print 'bcd length', self.bcd_length
        print 'state instruction length', self.state_instruction_length
        print 'ind len', len(self.chromosome)

        print 'pre-mutated individual', self.chromosome

        prev_num_states = self.num_states

        # set num_states to a power of 2 either above or below the current num_states
        self.num_states = int(choice( [(log(self.num_states,2)-1)**2, ((log(self.num_states,2)+1)**2)-1] ))

        # keep bcd_length at 1 or more
        if self.num_states < 2:
            self.num_states = 2
            return

        state_diff = self.num_states - prev_num_states

        # calculate whether we need to add/remove a binary digit
        digit_diff = len(bin(self.num_states)) - len(bin(prev_num_states))

        print 'state_diff', state_diff
        print 'digit_diff', digit_diff

        # add or remove a state instruction

        if state_diff > 0:
            for _ in range(state_diff):
                print 'adding a state'
                # add a state instruction
                # each state consists of a probability to cooperate and two BCDs.
                self.chromosome.append(self.generate_random_prob())
                print 'after appending choice prob', self.chromosome
                for i in range(2): # just do this twice
                    self.chromosome.extend(self.generate_random_state())
                    print 'after extending', self.chromosome
        elif state_diff < 0:
            for _ in range(-state_diff):
                print 'removing a state'
                # remove the last state instruction
                del(self.chromosome[ len(self.chromosome)-self.state_instruction_length : len(self.chromosome) ])

        # recalculate bcd_length and state_instruction_length
        self.recalculate_attributes()

        print 'num states', self.num_states
        print 'bcd length', self.bcd_length
        print 'state instruction length', self.state_instruction_length
        print 'ind len', len(self.chromosome)

        print '  after changing state', self.chromosome

        # WARNING: this next part is very fragile due to the precise inserting/deleting

        if digit_diff is not 0:
            state_locations = [] # used to keep track of where we will insert/delete a digit

            # first find all the locations at which we need to add/remove a digit

            index = 0 # we need to change the initial state
            state_locations.append(index)
            index += self.bcd_length # move past the initial state so we start at the first state instruction
            while index < len(self.chromosome):
                # we start at the start of the state instruction
                for i in range(2): # there are two state transition instructions
                    state_locations.append(index)
                    index += self.bcd_length # move to the start of the state transition instruction
                index += ACTION_PROB_LEN # move to the start of the next state instruction

            print state_locations

            # now add/remove digits

            if digit_diff > 0:
                print 'adding a digit'
                for i in range(len(state_locations)):
                    self.chromosome.insert(state_locations[i], 0) # insert a 0 here so we don't change the state number
                    state_locations = [j+1 for j in state_locations] # add 1 to all the locations because we added 1 to len(individual)
            elif digit_diff < 0:
                print 'removing a digit'
                for i in range(len(state_locations)):
                    #print state_locations
                    #print self.chromosome
                    del(self.chromosome[state_locations[i]]) # remove the digit here
                    state_locations = [j-1 for j in state_locations] # subtract 1 from all the locations because we subtracted 1 from len(individual)

        print 'num states', self.num_states
        print 'bcd length', self.bcd_length
        print 'state instruction length', self.state_instruction_length
        print 'ind len', len(self.chromosome)

        print '    mutated individual', self.chromosome

    def find_current_position(self, state):
        return self.bcd_length + self.state_instruction_length * state # the self.bcd_length is for the initial state part at the start

    def find_next_state(self, state, opponent_move_history):
        state_locator_index = 0 # the index of the state we're going to move to

        # put a 0 or a 1 at each decimal place for whether the opponent cooperated or defected
        for i in xrange(len(opponent_move_history)):
            state_locator_index += 10**i * int(opponent_move_history[i])

        # treat state_locator_index as a literal binary number, then convert it to base 10 so we can use it as an actual index
        state_locator_index = int('0b'+str(state_locator_index), 2)

        #print "current position == ", self.find_current_position(state)
        #print "state_locator_index == ", state_locator_index

        # find the state at state_locator_index
        start = self.find_current_position(state) + ACTION_PROB_LEN + state_locator_index * self.bcd_length
        end = start + self.bcd_length

        #print "self.chromosome == ", self.chromosome
        #print "next state == ", list_to_number(self.chromosome[start:end])
        # return the state as a decimal number
        return list_to_number(self.chromosome[start:end])

    def find_initial_state(self):
        # BCD_length is the length of a binary representation of a state of the individual.
        # individual[:BCD_length] is, therefore, the initial state of the individual in list form.
        # We need to convert it to a number to work with, so we use list_to_number().
        #print 'initial state', list_to_number(self.chromosome[:self.bcd_length])
        return list_to_number(self.chromosome[:self.bcd_length])

    #def split_into_states(self, individual):
    #    """We have an initial state at the beginning, so skip over that."""
    #    for i in xrange(self.bcd_length, len(individual), self.state_instruction_length):
    #        yield 1 + list_to_number(individual[i:i+self.state_instruction_length])

    def get_graph_info(self, state):
        cooperation_prob = round(self.calculate_cooperation_probability(state), 3)

        # this next line creates a list of all the possible move histories we can see according to our memory
        histories_list = map(lambda x: x.zfill(self.memory), map(lambda x: x[2:], map(bin, range(2**self.memory))))

        for opponent_move_history in histories_list:
            yield (state, self.find_next_state(state, opponent_move_history)), str(opponent_move_history), str(cooperation_prob)