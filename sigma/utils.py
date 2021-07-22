
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os
import pickle

def save_data(data, filename):
	'''
	Saves data (pickle dump) into specified file

	Parameters
	----------
	data: object
		The data that is to be saved
	filename: str
		The path and name of file for the serialized data
	'''
	
	os.makedirs(os.path.dirname(filename), exist_ok=True)
	with open(filename, 'wb') as f:
		pickle.dump(data, f)

def open_data(filename):
	'''
	Loads data (pickle load) from specified file

	Parameters
	----------
	filename: str
		The path and name of file of the serialized data

	Returns
	-------
	object
		The reconstituted object from its pickled representation
	'''

	with open(filename, 'rb') as f:
		return pickle.load(f)

def print_graph(structure, filename):
	'''
	Prints graphical depiction of the population structure

	Parameters
	----------
	structure: networkx.classes.graph.Graph
		The spatial structure of the population
	filename: str
		The path and name of file for the output image
	'''

	f = plt.figure(figsize=(10, 10))
	node_colors = np.zeros((structure.number_of_nodes(), 3))
	for i in range(0, structure.number_of_nodes()):
		if np.random.rand()<(1/2):
			node_colors[i, :] = np.array([0.6, 0, 0])
		else:
			node_colors[i, :] = np.array([0, 0, 0.6])
	nx.draw(structure, pos=nx.spring_layout(structure, iterations=1000), 
		node_color=node_colors, node_size=250, edge_color='grey')
	os.makedirs(os.path.dirname(filename), exist_ok=True)
	f.savefig(filename, bbox_inches='tight', transparent=True)