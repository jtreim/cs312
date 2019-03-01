#!/usr/bin/python3


from CS312Graph import *
import time
import abc


class PriorityQueue(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        pass
    
    @abc.abstractmethod
    def makeQueue(self, values):
        pass
    
    @abc.abstractmethod
    def insert(self, value, priority):
        pass

    @abc.abstractmethod
    def deleteMin(self):
        pass

    @abc.abstractmethod
    def decreaseKey(self, value):
        pass

    @abc.abstractmethod
    def empty(self):
        pass


class UnsortedListPriorityQueue(PriorityQueue):
    def __init__(self):
        self.list = []

    def makeQueue(self, values):
        for value in values:
            self.list.append((value,value.dist))

    def insert(self, value):
        self.list.append((value, value.dist))

    def deleteMin(self):
        min = self.list[0]
        min_idx = 0
        for idx, pair in enumerate(self.list):
            if min[1] > pair[1]:
                min = pair[1]
                min_idx = idx
        del self.list[min_idx]
        return min

    def decreaseKey(self, value):
        self.list[idx] = (value, value.dist)

    def empty(self):
        return len(self.list) == 0


class NetworkRoutingSolver:
    def __init__( self ):
        pass

    def initializeNetwork( self, network ):
        assert( type(network) == CS312Graph )
        self.network = network

    def getShortestPath( self, destIndex ):
        self.dest = destIndex

        # TODO: RETURN THE SHORTEST PATH FOR destIndex
        #       INSTEAD OF THE DUMMY SET OF EDGES BELOW
        #       IT'S JUST AN EXAMPLE OF THE FORMAT YOU'LL 
        #       NEED TO USE

        path_edges = []
        total_length = 0
        node = self.network.nodes[self.source]
        edges_left = 3
        while edges_left > 0:
            edge = node.neighbors[2]
            path_edges.append( (edge.src.loc, edge.dest.loc, '{:.0f}'.format(edge.length)) )
            total_length += edge.length
            node = edge.dest
            edges_left -= 1
        return {'cost':total_length, 'path':path_edges}

    def dijkstra(self, srcIndex, use_heap=False):
        queue = UnsortedListPriorityQueue()
        for vertex in vertices:
            vertex.dist = float('inf')
            vertex.prev = None
        queue.makeQueue(vertices)
        start_vertex.dist = 0
        start_vertex.prev = start_vertex
        queue.decreaseKey(start_vertex)
        

        while not queue.empty():
            vertex = queue.deleteMin()
            for edge in vertex.edges:
                if edge.length + vertex.dist < edge.other.dist:
                    edge.other.dist = edge.length + vertex.dist






    def computeShortestPaths( self, srcIndex, use_heap=False ):
        self.source = srcIndex
        t1 = time.time()

        # TODO: RUN DIJKSTRA'S TO DETERMINE SHORTEST PATHS.
        #       ALSO, STORE THE RESULTS FOR THE SUBSEQUENT
        #       CALL TO getShortestPath(dest_index)


        t2 = time.time()
        return (t2-t1)

