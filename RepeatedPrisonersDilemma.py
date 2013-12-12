'''
Created on Mar 8, 2013

@author: Daniel Horowitz
'''
from Environment import Environment
from RPD_Individual import RPD_Individual
from globals import NUM_GAME_REPETITIONS

class RepeatedPrisonersDilemma(Environment):
    def __init__(self):
        self.individual = RPD_Individual
        
    def prisoners_dilemma(self, move1, move2):
        # reward matrix:
        #     C2    D2
        # C1 (3,3) (0,5)
        # D1 (5,0) (1,1)
        
        # 0 = cooperate, 1 = defect
        
        # just return player 1's reward
        
        if move1==1 and move2==1:
            return 1
        elif move1==1 and move2==0:
            return 5
        elif move1==0 and move2==1:
            return 0
        elif move1==0 and move2==0:
            return 3
        else:
            print "illegal moves have been made :("
            raise Exception

    def main(self, player, opponents):
        # opponents is a list of players; may contain 1 or more.
        # player == chromosome
        reward_sum = 0 # keep track of the total reward
        
        for opponent in opponents:
            player_state = player.find_initial_state()
            opponent_state = opponent.find_initial_state()
            
            for _ in range(NUM_GAME_REPETITIONS):
                # add our current moves
                player.move_history.append(player.find_move(player_state))
                opponent.move_history.append(opponent.find_move(opponent_state))

                # forget the oldest move if we can't remember any more
                if len(player.move_history) > opponent.memory:
                    del player.move_history[0]
                if len(opponent.move_history) > player.memory:
                    del opponent.move_history[0]

                # this is the current move
                player_current_move = player.move_history[-1]
                opponent_current_move = opponent.move_history[-1]
                
                # get our reward
                reward_sum += self.prisoners_dilemma(player_current_move, opponent_current_move)
                
                # move to the next state
                player_state = player.find_next_state(player_state, opponent.move_history)
                opponent_state = opponent.find_next_state(opponent_state, player.move_history)
        
        return float(reward_sum) / float(NUM_GAME_REPETITIONS * len(opponents)) # average reward is much more interesting than total reward