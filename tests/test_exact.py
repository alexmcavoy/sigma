
import networkx as nx
import numpy as np
import unittest
import sigma.exact as exact

class TestExactMethods(unittest.TestCase):

	def setUp(self):
		self.structure = nx.karate_club_graph()
		self.mutation_rate = 0.1
		self.tol = 4
		self.w, self.A, self.e, self.d = exact.random_walk_probabilities(self.structure)

	def test_location_weights(self):
		tilde_v = self.d*exact.location_weights(self.e, self.d, self.mutation_rate)
		x = np.ones((self.e.shape[0],))
		y = np.asarray(self.e.shape[0]*tilde_v@(np.eye(self.e.shape[0])-(1-self.mutation_rate)*self.A)).ravel()
		self.assertEqual(np.round(x, self.tol).tolist(), np.round(y, self.tol).tolist())

	def test_identity_by_state_probabilities_spsolve(self):
		x = exact.identity_by_state_probabilities(self.A, self.mutation_rate, 'spsolve')
		y = self.mutation_rate/2 + ((1-self.mutation_rate)/2)*(self.A@x+(self.A@x).T)
		np.fill_diagonal(y, np.ones((self.A.shape[0],)))
		self.assertEqual(np.round(x, self.tol).tolist(), np.round(y, self.tol).tolist())

	def test_identity_by_state_probabilities_lsqr(self):
		x = exact.identity_by_state_probabilities(self.A, self.mutation_rate, 'lsqr')
		y = self.mutation_rate/2 + ((1-self.mutation_rate)/2)*(self.A@x+(self.A@x).T)
		np.fill_diagonal(y, np.ones((self.A.shape[0],)))
		self.assertEqual(np.round(x, self.tol).tolist(), np.round(y, self.tol).tolist())

if __name__ == '__main__':
	unittest.main()
