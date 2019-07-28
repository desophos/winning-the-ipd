'''
Created on Mar 3, 2013
'''

from globals import *
from evolution import evolution
from RepeatedPrisonersDilemma import RepeatedPrisonersDilemma
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import numpy

"""
import igraph

def plot_FSA_graph(fsa, fsa_manager):
    g = igraph.Graph(directed=True)

    color_dict = {'0':"green",  # opponent cooperates
                  '1':"red"  # opponent defects
                  }

    g.add_vertices([str(s) for s in range(fsa.num_states)])  # add each state as a vertex

    for v in g.vs():
        for edge, label in fsa_manager.get_graph_info(fsa, int(v["name"])):
            #print 'edge',edge
            # label == ('input','output')
            g.add_edge(edge[0], edge[1], color=color_dict[label[0]])  # color edge as opponent's move; see color_dict
            v["label"] = label[1]  # label vertex with my probability to cooperate

    #t = text.TextDrawer(, "Vertices are labeled with the output, edges are colored according to the input.")
    #t.draw(wrap=True)

    igraph.plot(g, layout=g.layout("kk"), vertex_size=50, edge_width=2)
"""


def plot_FSA_graph(fsa, fsa_manager):
    g = nx.MultiDiGraph()

    g.add_nodes_from([s for s in range(fsa.num_states)])  # add each state as a node

    node_labels = {}
    edge_labels = {}

    for n in g.nodes_iter():
        for edge, move_hist, coop_prob in fsa_manager.get_graph_info(fsa, int(n)):
            #print 'edge',edge
            g.add_edge(*edge)
            edge_labels[edge] = move_hist  # label edge with opponent's move history
            node_labels[int(n)] = coop_prob  # label node with my probability to cooperate

    pos = nx.circular_layout(g)

    nx.draw_networkx(g, pos, with_labels=False, node_size=1200)
    nx.draw_networkx_labels(g, pos, labels=node_labels, font_size=8)
    nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
    plt.show()


def analyze_expected_payoff(player, opponent):
    Sx = [3,0,5,1]  # player payoff vector
    Sy = [3,5,0,1]  # opponent payoff vector


def main():
    parser = argparse.ArgumentParser(description='Evolve populations.')
    parser.add_argument('fn', choices=['rpd', 'repeated_prisoners_dilemma'], help='the fitness function to use')
    parser.add_argument('-pop', '--populations_num', type=int, default=NUM_POPULATIONS, choices=[2], help='the number of populations to use')
    #parser.add_argument('-gen', '--generations_num', type=int, default=NUM_GENERATIONS, help='the number of generations to run')
    parser.add_argument('-ind', '--individuals_num', type=int, default=NUM_INDIVIDUALS, help='the number of individuals in each population')
    parser.add_argument('-prune', '--pruning_num', type=int, default=PRUNING_NUM, help='number of individuals to prune from each generation')
    parser.add_argument('-mut', '--mutations_num', type=int, default=NUM_GENE_MUTATIONS, help='number of genes to mutate')
    parser.add_argument('-mut_p', '--mutation_probability', type=float, default=MUTATION_PROBABILITY, help='probability to mutate each gene')
    parser.add_argument('-s_mut_p', '--structure_mutation_probability', type=float, default=STRUCTURE_MUTATION_PROBABILITY, help='probability to mutate the chromosome structure')

    args = vars(parser.parse_args(['rpd']))  # return args as a dict
    print(args)

    if args['fn'] in ['rpd', 'repeated_prisoners_dilemma']:
        environment = RepeatedPrisonersDilemma()

    populations = []
    for _ in range(args['populations_num']):
        populations.append(environment.generate_population())

    while True:
        g = int(raw_input("How many generations? "))
        if g <= 0:
            break
        populations = evolution(populations, environment.main, environment.individual, g, args)

    for population in populations:
        # the first individual in each population is the most fit
        plot_FSA_graph(population[0], environment.individual)


if __name__ == '__main__':
    main()
