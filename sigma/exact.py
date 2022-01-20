
import networkx as nx
import numpy as np
import os
from joblib import Parallel, delayed
from scipy import sparse as sp

def run_calculations(structure, b, c, mutation_rates, solver='spsolve', verbose=False):
	'''
	Main calculation runner

	Parameters
	----------
	structure: networkx.classes.graph.Graph
		The spatial structure of the population
	b: float
		The benefit generated by producers 
	c: float
		The cost incurred by producers
	mutation_rates: numpy.ndarray
		The per-capita mutation probabilities
	solver: str
		The numerical solver for identity by state
	verbose: bool
		Whether to print each mutation rate as it is being simulated (default: False)

	Returns
	-------
	numpy.ndarray
		An array of the first-order selection effects for ff-goods, one for each mutation rate
	numpy.ndarray
		An array of the first-order selection effects for pp-goods, one for each mutation rate
	'''

	def run_single_calculation(mutation_rate):
		if verbose:
			print(mutation_rate)
		K1, K2, w, A = structure_coefficients(structure, mutation_rate, solver)
		ff = frequency_derivative(K1, K2, w, A, b, c, 'ff')
		pp = frequency_derivative(K1, K2, w, A, b, c, 'pp')
		return ff, pp

	# run calculations in parallel, using the maximum number of cpu cores
	selection_effects = np.asarray(Parallel(n_jobs=os.cpu_count())(
		delayed(run_single_calculation)(mutation_rate) for mutation_rate in mutation_rates))
	return selection_effects[:, 0], selection_effects[:, 1]

def random_walk_probabilities(structure):
	'''
	Calculates the adjacency matrix, the ancestral random walk, the marginal transmission
	probabilities, and the death probabilities

	Parameters
	----------
	structure: networkx.classes.graph.Graph
		The spatial structure of the population

	Returns
	-------
	scipy.sparse.csr.csr_matrix
		The adjacency matrix for the structure
	scipy.sparse.csr.csr_matrix
		The transition matrix for the ancestral random walk
	scipy.sparse.csc.csc_matrix
		A matrix of the marginal transmission probabilities
	numpy.ndarray
		A vector of the death probabilities, one for each location
	'''

	w = nx.adjacency_matrix(structure)
	A = w.multiply(sp.csr_matrix(1/np.sum(w, axis=1)))
	e = A.transpose()/A.shape[0]
	d = np.asarray(np.sum(e, axis=0)).ravel()
	return w, A, e, d

def location_weights(e, d, mutation_rate):
	'''
	Calculates mutation-weighted reproductive values

	Parameters
	----------
	e: scipy.sparse.csc.csc_matrix
		A matrix of the marginal transmission probabilities
	d: numpy.ndarray
		A vector of the death probabilities, one for each location
	mutation_rate: float
		The per-capita mutation probability

	Returns
	-------
	numpy.ndarray
		The vector of mutation-weighted reproductive values
	'''

	population_size = e.shape[0]
	tilde_A = sp.eye(population_size, format='csr')-(1-mutation_rate)*(
		e.transpose().multiply(sp.csr_matrix(1/np.transpose(d))))
	tilde_v = sp.linalg.spsolve(tilde_A.transpose(), 
		mutation_rate*np.ones((population_size, 1))/population_size)
	return np.divide(tilde_v.transpose(), d)

def identity_by_state_probabilities(A, mutation_rate, solver):
	'''
	Calculates probabilities of identity by state under neutral drift

	Parameters
	----------
	A: scipy.sparse.csr.csr_matrix
		The transition matrix for the ancestral random walk
	mutation_rate: float
		The per-capita mutation probability
	solver: str
		The numerical solver for identity by state

	Returns
	-------
	numpy.ndarray
		The matrix of pairwise identity-by-state probabilities
	'''

	population_size = A.shape[0]
	M = sp.eye(population_size**2, format='csr')-(1-mutation_rate)*(1/2)*(sp.kron(sp.eye(
		population_size, format='csr'), A)+sp.kron(A, sp.eye(population_size, format='csr')))
	b = mutation_rate*(1/2)*np.ones([population_size**2, 1])
	for i in range(0, population_size):
		row = i*population_size+i
		M[row, M[row, :].nonzero()[1]] = 0
		M[row, row] = 1
		b[row] = 1
	if not isinstance(solver, str):
		raise TypeError('Solver must be a string.')
	elif not solver.lower() in ['spsolve', 'lsqr']:
		raise ValueError('Solver must be \'spsolve\' or \'lsqr\'.')
	if solver.lower()=='spsolve':
		x = sp.linalg.spsolve(M, b)
	else:
		x = sp.linalg.lsqr(M, b)[0]
	x = np.reshape(x, (population_size**2, 1))
	return x.reshape((population_size, population_size), order='F')

def marginal_fecundity_effects(A):
	'''
	Calculates marginal fecundity effects

	Parameters
	----------
	A: scipy.sparse.csr.csr_matrix
		The transition matrix for the ancestral random walk

	Returns
	-------
	dict
		The effects of fecundities on marginal transmission probabilities
	'''

	population_size = A.shape[0]
	m = {}
	for i in range(0, population_size):
		m[i] = -A.multiply(A[:, i])/population_size
		m[i][:, i] = m[i][:, i] + A[:, i]/population_size
	return m

def structure_coefficients(structure, mutation_rate, solver):
	'''
	Calculates the structure coefficients

	Parameters
	----------
	structure: networkx.classes.graph.Graph
		The spatial structure of the population
	mutation_rate: float
		The per-capita mutation probability
	solver: str
		The numerical solver for identity by state

	Returns
	-------
	numpy.ndarray
		The matrix of structure coefficients, K1
	numpy.ndarray
		The matrix of structure coefficients, K2
	numpy.ndarray
		The dense representation of the adjacency matrix
	numpy.ndarray
		The dense representation of the ancestral random walk
	'''

	w, A, e, d = random_walk_probabilities(structure)
	m = marginal_fecundity_effects(A)
	v = location_weights(e, d, mutation_rate).reshape(1, -1)
	phi = identity_by_state_probabilities(A, mutation_rate, solver)
	K1, K2 = np.zeros(e.shape), np.zeros(e.shape)
	for j in range(0, e.shape[0]):
		mj = np.asarray(m[j].todense())
		term1 = (v@(mj*phi)).T
		term2 = ((((v.T)*mj)).T)@phi
		term3 = ((v@mj)*phi[j, :].reshape(1, -1)).T
		term4 = ((v@mj).T)@phi[j, :].reshape(1, -1)
		term5 = np.sum(v@mj)/e.shape[0]
		K1 += (1/(2*mutation_rate))*(-(term1+term2)+(1-mutation_rate)*(term3+term4)+term5)
		K2 += (1/(2*mutation_rate))*(-(term1-term2)+(1-mutation_rate)*(term3-term4))
	return K1, K2, np.asarray(w.todense()), np.asarray(A.todense())

def frequency_derivative(K1, K2, w, A, b, c, social_good):
	'''
	Calculates the first-order effects of selection on mean frequencies

	Parameters
	----------
	K1: numpy.ndarray
		The matrix of structure coefficients, K1
	K2: numpy.ndarray
		The matrix of structure coefficients, K2
	w: numpy.ndarray
		The adjacency matrix for the structure
	A: numpy.ndarray
		The transition matrix for the ancestral random walk
	b: float
		The benefit generated by producers 
	c: float
		The cost incurred by producers
	social_good: str
		The social good ('ff' or 'pp') being produced 

	Returns
	-------
	float
		The first derivative of the mean frequency of producers with respect to selection intensity
	'''

	if not isinstance(social_good, str):
		raise TypeError('Social good must be a string.')
	elif not social_good.lower() in ['ff', 'pp']:
		raise ValueError('Social good must be \'ff\' or \'pp\'.')
	if social_good.lower()=='ff':
		return (1/2)*(np.sum(np.diag(A@(K1-K2)))*b-np.sum(np.diag((A.T)@(K1+K2)))*c)
	else:
		K1_pp, K2_pp = np.sum(np.multiply(K1, w)), np.sum(np.multiply(K2, w))
		return (1/2)*((K1_pp-K2_pp)*b-(K1_pp+K2_pp)*c)
