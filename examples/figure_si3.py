
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os
import sys
import time

import sigma.exact as exact

from sigma.simulation import run_simulations
from sigma.utils import *

def produce_panel_for_figure_si3(selection_intensities, input_directory, output_directory):
	'''
	Generates data and plots panels for Figure SI3

	Parameters
	----------
	selection_intensities: list
		The list of selection intensities to run
	input_directory: str
		The path of the input directory
	output_directory: str
		The path of the output directory
	'''

	mutation_rates_simulation = open_data(os.path.join(input_directory, 'mutation_rates_simulation.pickle'))
	
	for good_type in ['ff', 'pp']:
		# plot exact and simulation results together
		f = plt.figure(figsize=(10, 10))
		plt.axhline(y=0.5, xmin=0, xmax=1, color=(0, 0, 0), linestyle='--')
		for selection_intensity in selection_intensities:
			simulation_data = open_data(os.path.join(input_directory, 'selection_intensities/{:e}/'.format(selection_intensity)+good_type+'-goods/simulation.pickle'))
			plt.scatter(mutation_rates_simulation, simulation_data, label='$\delta = $'+'{}'.format(selection_intensity))
		plt.xticks(fontsize=20)
		plt.yticks([0, 0.25, 0.5, 0.75, 1], fontsize=20)
		plt.xlim([0, 1])
		plt.ylim([0, 1])
		plt.grid()
		plt.legend(fontsize=20, loc='upper center', markerscale=2.0)
		os.makedirs(os.path.dirname(output_directory), exist_ok=True)
		f.savefig(os.path.join(output_directory, good_type+'-goods_dataplot.pdf'), bbox_inches='tight')

if __name__=='__main__':
	# input directories
	ba_input_directory = 'data/figure_si2/barabasi-albert/'
	er_input_directory = 'data/figure_si2/erdos-renyi/'
	
	# output directories
	ba_output_directory = 'results/figure_si3/barabasi-albert/'
	er_output_directory = 'results/figure_si3/erdos-renyi/'

	selection_intensities = [0.05, 0.20, 0.50] # selection intensities

	print('Producing panel(s) for BA graph.')
	produce_panel_for_figure_si3(selection_intensities, ba_input_directory, ba_output_directory)

	print('Producing panel(s) for ER graph.')
	produce_panel_for_figure_si3(selection_intensities, er_input_directory, er_output_directory)
