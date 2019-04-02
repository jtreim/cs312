#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time
import numpy as np
from TSPClasses import *
import heapq
import itertools

from timeout import timeout


class ReducedCostMatrix:
	def __init__(self, matrix, visited, lower_bound=0):
		self.matrix = matrix.copy()
		self.lower_bound = lower_bound
		self.visited = visited
		for row in range(len(matrix[:,0])):
			min_value = np.min(matrix[row,:])
			if min_value != np.inf and min_value > 0:
				self.matrix[row,:] -= min_value
				self.lower_bound += min_value
		
		for col in range(len(matrix[0,:])):
			min_value = np.min(self.matrix[:,col])
			if min_value != np.inf and min_value > 0:
				self.matrix[:,col] -= min_value
				self.lower_bound += min_value
	
	def num_visited(self):
		return len(self.visited)

	def get_children(self):
		children = []
		current_city = self.visited[-1]
		for i in range(len(self.matrix[0,:])):
			if self.matrix[current_city, i] != np.inf:
				lower_bound = self.lower_bound + self.matrix[current_city, i]
				child_matrix = self.matrix.copy()
				child_matrix[current_city,:].fill(np.inf)
				child_matrix[:,i].fill(np.inf)
				child_matrix[i, current_city] = np.inf
				visited = self.visited.copy()
				visited.append(i)
				child = ReducedCostMatrix(child_matrix, visited,
										  lower_bound=lower_bound)
				children.append(child)
		return children

	def can_return_home(self):
		return np.min(self.matrix[:,0]) != np.inf

	def __lt__(self, other):
		if len(self.visited) != len(other.visited):
			return len(self.visited) > len(other.visited)
		return self.lower_bound < other.lower_bound
	
	def __str__(self):
		result = ('lower_bound: %s, len_visited: %s, current: %s\n' %
				  (self.lower_bound, len(self.visited), self.visited[-1]))
		for r in range(len(self.matrix[:,0])):
			row = '[ '
			for c in range(len(self.matrix[0,:])):
				row += '{:^7}'.format(self.matrix[r,c])
			row += ' ]\n'
			result += row
		return result


class TSPSolver:
	def __init__( self, gui_view ):
		self._scenario = None

	def setupWithScenario( self, scenario ):
		self._scenario = scenario


	''' <summary>
		This is the entry point for the default solver
		which just finds a valid random tour.  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of solution, 
		time spent to find solution, number of permutations tried during search, the 
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''
	
	def defaultRandomTour( self, time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)
		foundTour = False
		count = 0
		bssf = None
		start_time = time.time()
		while not foundTour and time.time()-start_time < time_allowance:
			# create a random permutation
			perm = np.random.permutation( ncities )
			route = []
			# Now build the route using the random permutation
			for i in range( ncities ):
				route.append( cities[ perm[i] ] )
			bssf = TSPSolution(route)
			count += 1
			if bssf.cost < np.inf:
				# Found a valid route
				foundTour = True
		end_time = time.time()
		results['cost'] = bssf.cost if foundTour else math.inf
		results['time'] = end_time - start_time
		results['count'] = count
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		return results


	''' <summary>
		This is the entry point for the greedy solver, which you must implement for 
		the group project (but it is probably a good idea to just do it for the branch-and
		bound project as a way to get your feet wet).  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found, the best
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''

	def greedy( self,time_allowance=60.0 ):
		pass
	
	
	def construct_matrix(self):
		cities = self._scenario.getCities()
		n_cities = len(cities)
		matrix = np.zeros((n_cities, n_cities))
		for a in cities:
			for b in cities:
				if a._index == b._index:
					matrix[a._index][b._index] = np.inf
				else:
					cost = a.costTo(b)
					matrix[a._index][b._index] = cost
		return matrix


	''' <summary>
		This is the entry point for the branch-and-bound algorithm that you will implement
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number solutions found during search (does
		not include the initial BSSF), the best solution found, and three more ints: 
		max queue size, total number of states created, and number of pruned states.</returns> 
	'''
				

	def branchAndBound( self, time_allowance=60.0 ):
		bssf = self.defaultRandomTour(time_allowance)
		soln_count = 0
		pruned = 0
		max_queue = 1
		queue = []
		start_time = time.time()
		total = 1
		matrix = self.construct_matrix()
		reduced = ReducedCostMatrix(matrix, [0])
		heapq.heappush(queue, reduced)
		max_city_count = len(self._scenario.getCities())
		cities = self._scenario.getCities()

		while len(queue) > 0 and time.time()-start_time < time_allowance:
			if len(queue) > max_queue:
				max_queue = len(queue)
			# print('\n__________________Queue______________________')
			# route_list = []
			# for city in bssf['soln'].route:
			# 	route_list.append(city._name)
			# print('bssf:%s cost:%s' % (route_list, bssf['cost']))
			# for branch in queue:
			# 	print(branch)

			next_branch = heapq.heappop(queue)
			
			# Pruning
			# The next branch is too big
			if next_branch.lower_bound >= bssf['cost']:
				pruned += 1
			# Branch is back at first city too early
			elif (next_branch.num_visited() < max_city_count and
				  next_branch.visited.count(0) == 2):
				pruned += 1
			# Branch has no way to return to first city
			elif not next_branch.can_return_home():
				pruned += 1

			# Found a possible solution
			elif next_branch.num_visited() == max_city_count:
				if next_branch.lower_bound < bssf['cost']:
					bssf['cost'] = next_branch.lower_bound
					
					route = []
					for idx in next_branch.visited:
						route.append(cities[idx])
					bssf['soln'] = TSPSolution(route)
				else:
					soln_count += 1
					pruned += 1

			# Keep branching
			else:
				children = next_branch.get_children()
				total += len(children)
				for child in children:
					heapq.heappush(queue, child)

		bssf['pruned'] = pruned
		bssf['max'] = max_queue
		bssf['time'] = time.time() - start_time
		bssf['total'] = total
		bssf['count'] = soln_count

		return bssf



	''' <summary>
		This is the entry point for the algorithm you'll write for your group project.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found during search, the 
		best solution found.  You may use the other three field however you like.
		algorithm</returns> 
	'''
		
	def fancy( self,time_allowance=60.0 ):
		pass
		



