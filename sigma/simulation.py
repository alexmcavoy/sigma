
import networkx as nx
import numpy as np
import os
from joblib import Parallel, delayed

def run_simulations(structure, social_good, b, c, mutation_rates, 
	selection_intensity, number_of_updates, trait=1, verbose=False):
	'''
	Main simulation runner

	Parameters
	----------
	structure: networkx.classes.graph.Graph
		The spatial structure of the population
	social_good: str
		The social good ('ff' or 'pp') being produced
	b: float
		The benefit generated by producers 
	c: float
		The cost incurred by producers
	mutation_rates: numpy.ndarray
		The per-capita mutation probabilities
	selection_intensity: float
		The intensity of selection
	number_of_updates: int
		The number of times to update the population
	trait: int
		The trait value under consideration (default: 1)
	verbose: bool
		Whether to print each mutation rate as it is being simulated (default: False)

	Returns
	-------
	numpy.ndarray
		An array of the mean frequencies of the trait, one for each mutation rate
	'''

	def run_single_simulation(mutation_rate):
		if verbose:
			print(mutation_rate)
		state = np.random.randint(0, 2, nx.number_of_nodes(structure))
		pop = Population(structure, state, social_good, b, c, mutation_rate, selection_intensity)
		return np.mean(pop.update_population(trait, number_of_updates))
	
	# run simulations in parallel, using the maximum number of cpu cores
	simulated_selection_effects = np.asarray(Parallel(n_jobs=os.cpu_count())(
		delayed(run_single_simulation)(mutation_rate) for mutation_rate in mutation_rates))
	return simulated_selection_effects

class Population(object):

	def __init__(self, structure, state, social_good, b, c, mutation_rate, selection_intensity):
		'''
		Initializes the population

		Parameters
		----------
		structure: networkx.classes.graph.Graph
			The spatial structure of the population 
		state: numpy.ndarray
			The state of the population (configuration of traits) 
		social_good: str
			The social good ('ff' or 'pp') being produced 
		b: float
			The benefit generated by producers 
		c: float
			The cost incurred by producers 
		mutation_rate: float
			The per-capita mutation probability 
		selection_intensity: float
			The intensity of selection
		'''

		# set the spatial structure and population size (number of nodes in the graph)
		self._structure = structure
		self._population_size = nx.number_of_nodes(structure)

		# set the initial state, meaning a configuration of traits
		if len(state)!=self._population_size:
			raise ValueError('Each individual must have a state.')
		self._state = state
		
		# set the type of social good produced in the population, as well as the benefit and cost
		if not isinstance(social_good, str):
			raise TypeError('Social good must be a string.')
		elif not social_good.lower() in ['ff', 'pp']:
			raise ValueError('Social good must be \'ff\' or \'pp\'.')
		self._social_good = social_good.lower()
		self._b = b
		self._c = c
		
		# set the per-capita mutation probability
		if not (isinstance(mutation_rate, float) 
			or isinstance(mutation_rate, int)):
			raise TypeError('Mutation rate must be a real number.')
		elif mutation_rate<0 or mutation_rate>1:
			raise ValueError('Mutation rate must be in [0, 1].')
		self._mutation_rate = mutation_rate
		
		# set the selection intensity
		if not (isinstance(selection_intensity, float) 
			or isinstance(selection_intensity, int)):
			raise TypeError('Selection intensity must be a real number.')
		elif selection_intensity<0:
			raise ValueError('Selection intensity must be non-negative.')
		self._selection_intensity = selection_intensity

	def mean_frequency(self, trait):
		'''
		Calculates the mean frequency of a trait in the population

		Parameters
		----------
		trait: int
			The trait value under consideration
		
		Returns
		-------
		float
			The mean frequency of the trait in the current state of the population
		'''

		return len([key for key, val in enumerate(self._state) 
			if val==trait])/self._population_size

	def payoff(self, subset):
		'''
		Calculates the payoffs for a subset of the population

		Parameters
		----------
		subset: list
			The subset of individuals whose payoff is to be calculated

		Returns
		-------
		numpy.ndarray
			The payoffs corresponding to the individuals in the subset
		'''

		payoffs = np.zeros((len(subset),))
		for individual in subset:
			neighbors = list(nx.neighbors(self._structure, individual))
			if self._social_good=='ff':
				payoffs[subset.index(individual)] = self._state[individual]*(-self._c) + sum([self._state[neighbor]
					*(self._b/nx.degree(self._structure, neighbor)) for neighbor in neighbors])
			else:
				payoffs[subset.index(individual)] = self._state[individual]*(-self._c*nx.degree(self._structure, 
					individual)) + sum([self._state[neighbor]*(self._b) for neighbor in neighbors])
		return payoffs

	def update_population(self, trait=None, number_of_updates=1):
		'''
		Updates the population using a death-birth rule

		Parameters
		----------
		trait: int
			The trait value under consideration (default: None)
		number_of_updates: int
			The number of times to update the population (default: 1)

		Returns
		-------
		numpy.ndarray
			An array of the mean frequencies of the trait after each update (or no return if no trait specified)
		'''
		
		mean_frequencies = np.zeros((number_of_updates,))
		for update in range(0, number_of_updates):
			# select individual for death, uniformly at random from the population
			death = np.random.randint(self._population_size)

			# find neighbors of deceased individual in the graph, as well as their payoffs and fitness
			neighbors = list(nx.neighbors(self._structure, death))
			neighbor_payoffs = self.payoff(neighbors)
			neighbor_fitness = np.exp(self._selection_intensity*
				(neighbor_payoffs-np.max(neighbor_payoffs)))

			# select a neighbor for reproduction, with probability proportional to fitness
			birth = np.random.choice(neighbors, p=neighbor_fitness/np.sum(neighbor_fitness))

			# subject the offspring to mutation
			if np.random.rand()<self._mutation_rate/2:
				self._state[death] = 1-self._state[birth]
			else:
				self._state[death] = self._state[birth]
			mean_frequencies[update] = self.mean_frequency(trait)
		return mean_frequencies if trait!=None else None
