
import networkx as nx
import numpy as np
import unittest
from sigma.simulation import Population

class TestPopulation(unittest.TestCase):

	def setUp(self):
		self.structure = nx.karate_club_graph()
		self.state = np.asarray([1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 
			1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1])
		self.social_good = 'ff'
		self.b = 2
		self.c = 1
		self.mutation_rate = 0.1
		self.selection_intensity = 0.1
		self.pop = Population(self.structure, self.state, self.social_good, 
			self.b, self.c, self.mutation_rate, self.selection_intensity)

	def test_bad_state_length(self):
		bad_state = [0, 0]
		self.assertRaises(ValueError, lambda: Population(self.structure, bad_state, 
			self.social_good, self.b, self.c, self.mutation_rate, self.selection_intensity))

	def test_bad_social_good_type(self):
		bad_social_good_type = 1
		self.assertRaises(TypeError, lambda: Population(self.structure, self.state, 
			bad_social_good_type, self.b, self.c, self.mutation_rate, self.selection_intensity))

	def test_bad_social_good_value(self):
		bad_social_good_value = 'good'
		self.assertRaises(ValueError, lambda: Population(self.structure, self.state, 
			bad_social_good_value, self.b, self.c, self.mutation_rate, self.selection_intensity))

	def test_bad_mutation_rate_type(self):
		bad_mutation_rate_type = 'rate'
		self.assertRaises(TypeError, lambda: Population(self.structure, self.state, 
			self.social_good, self.b, self.c, bad_mutation_rate_type, self.selection_intensity))

	def test_bad_mutation_rate_value(self):
		bad_mutation_rate_value = 2
		self.assertRaises(ValueError, lambda: Population(self.structure, self.state, 
			self.social_good, self.b, self.c, bad_mutation_rate_value, self.selection_intensity))

	def test_bad_selection_intensity_type(self):
		bad_selection_intensity_type = 'intensity'
		self.assertRaises(TypeError, lambda: Population(self.structure, self.state, 
			self.social_good, self.b, self.c, self.mutation_rate, bad_selection_intensity_type))

	def test_bad_selection_intensity_value(self):
		bad_selection_intensity_value = -1
		self.assertRaises(ValueError, lambda: Population(self.structure, self.state, 
			self.social_good, self.b, self.c, self.mutation_rate, bad_selection_intensity_value))

	def test_mean_frequency(self):
		direct_calculation = np.sum(self.state)/self.structure.number_of_nodes()
		self.assertEqual(self.pop.mean_frequency(1), direct_calculation)

	def test_payoff(self):
		subset = [23, 31]
		direct_calculation = [self.b*(1/3+1/4+1/17), -self.c+self.b*(1/16+1/3+1/17)]
		payoffs = self.pop.payoff(subset)
		self.assertEqual(direct_calculation, payoffs.tolist())

if __name__ == '__main__':
	unittest.main()
