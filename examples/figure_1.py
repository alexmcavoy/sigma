
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os
import sys
import time

import sigma.exact as exact

from sigma.simulation import run_simulations
from sigma.utils import *

def produce_panel_for_figure_1(structure, b, c, mutation_rates_exact, 
	mutation_rates_simulation, selection_intensity, number_of_updates, directory):
	'''
	Generates data and plots panels for figure 1

	Parameters
	----------
	structure: networkx.classes.graph.Graph
		The spatial structure of the population
	b: float
		The benefit generated by producers 
	c: float
		The cost incurred by producers
	mutation_rates_exact: numpy.ndarray
		The per-capita mutation probabilities for exact calculations
	mutation_rates_simulation: numpy.ndarray
		The per-capita mutation probabilities for simulations
	selection_intensity: float
		The intensity of selection
	number_of_updates: int
		The number of times to update the population
	directory: str
		The path of the output directory
	'''
	
	for benefit in b:
		print('Running exact calculations for benefit %s.' % benefit)
		start_time = time.time()
		# run exact calculations (write 'lsqr' in place of 'spsolve' to use a least-squares solver)
		ff_exact, pp_exact = exact.run_calculations(structure, benefit, c, mutation_rates_exact, solver='spsolve')
		print('Total time taken: %s seconds.' % (np.round(time.time() - start_time, 3)))

		print('Running simulations for benefit %s and selection intensity %s.' % (benefit, selection_intensity))
		start_time = time.time()
		ff_simulation = run_simulations(structure, 'ff', benefit, c, mutation_rates_simulation, 
			selection_intensity, number_of_updates)
		pp_simulation = run_simulations(structure, 'pp', benefit, c, mutation_rates_simulation, 
			selection_intensity, number_of_updates)
		print('Total time taken: %s seconds.' % (np.round(time.time() - start_time, 3)))

		for data_type in ['exact', 'simulation']:
			for good_type in ['ff', 'pp']:
				if data_type=='simulation':
					first_order_effects = (locals()[good_type+'_'+data_type]-0.5)/selection_intensity
				else:
					first_order_effects = locals()[good_type+'_'+data_type]
				save_data(first_order_effects, os.path.join(directory, 
					'benefits/'+'{:e}'.format(benefit)+'/'+good_type+'-goods/'+data_type+'.pickle'))

		# plot exact and simulation results together
		f = plt.figure(figsize=(10, 10))
		plt.axhline(y=0, xmin=0, xmax=1, color=(0, 0, 0), linestyle='--')
		plt.plot(mutation_rates_exact, ff_exact, color=(0, 0.6, 0.6), linewidth=3)
		plt.plot(mutation_rates_exact, pp_exact, color=(0.6, 0, 0.6), linewidth=3)
		plt.scatter(mutation_rates_simulation, (ff_simulation-0.5)/selection_intensity, color=(0, 0.6, 0.6))
		plt.scatter(mutation_rates_simulation, (pp_simulation-0.5)/selection_intensity, color=(0.6, 0, 0.6))
		plt.xticks(fontsize=20)
		plt.yticks(fontsize=20)
		plt.xlim([0, 1])
		plt.grid()
		f.savefig(os.path.join(directory, 'benefits/'+'{:e}'.format(benefit)+'/dataplot.pdf'), bbox_inches='tight')

if __name__=='__main__':
	# output directories
	ba_directory = 'results/figure_1/barabasi-albert/'
	er_directory = 'results/figure_1/erdos-renyi/'
	if len(sys.argv)>1 and sys.argv[1]=='True':
		# load structures used to produce figure 1 in the text
		structure_ba = open_data('data/figure_1/barabasi-albert/structure.pickle') # barabasi-albert graph
		structure_er = open_data('data/figure_1/erdos-renyi/structure.pickle') # erdos-renyi graph
	else:
		# generate new structures
		N, m, p = 50, 1, 0.05

		structure_ba = nx.generators.random_graphs.barabasi_albert_graph(N, m) # barabasi-albert graph
		save_data(structure_ba, ba_directory+'structure.pickle')
		
		structure_er = nx.generators.random_graphs.erdos_renyi_graph(N, p) # erdos-renyi graph
		while not nx.is_connected(structure_er):
			structure_er = nx.generators.random_graphs.erdos_renyi_graph(N, p)
		save_data(structure_er, er_directory+'structure.pickle')

	print_graph(structure_ba, ba_directory+'structure.pdf')
	print_graph(structure_er, er_directory+'structure.pdf')

	number_of_points_exact = 1000 # number of mutation rates used for exact calculations
	number_of_points_simulation = 39 # number of mutation rates used for exact calculations
	number_of_updates = int(1e8) # number of updates used to take mean frequencies
	selection_intensity = 0.05 # selection intensity

	b = [0.9, 5] # benefits generated by producers
	c = 1 # cost incurred by producers

	mutation_rates_exact = np.linspace(1/number_of_points_exact, 1, number_of_points_exact)
	mutation_rates_simulation = np.linspace(1/(number_of_points_simulation+1), 
			1-1/(number_of_points_simulation+1), number_of_points_simulation)

	print('Producing panel for BA graph.')
	produce_panel_for_figure_1(structure_ba, b, c, mutation_rates_exact, 
		mutation_rates_simulation, selection_intensity, number_of_updates, ba_directory)

	print('Producing panel for ER graph.')
	produce_panel_for_figure_1(structure_er, b, c, mutation_rates_exact, 
		mutation_rates_simulation, selection_intensity, number_of_updates, er_directory)
