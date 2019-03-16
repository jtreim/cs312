#!/usr/bin/python3


from CS312Graph import *
import time
import abc

# Define abstract methods priority queues must implement 
class PriorityQueue(abc.ABC):
    def __init__(self):
        self.list = []
        self.list_idx = {}
    
    @abc.abstractmethod
    def makeQueue(self, nodes):
        pass
    
    @abc.abstractmethod
    def insert(self, entry):
        pass

    @abc.abstractmethod
    def deleteMin(self):
        pass

    @abc.abstractmethod
    def decreaseKey(self, changed):
        pass

    def empty(self):
        return 0 == len(self.list)


class PriorityQueueEntry:
    def __init__(self, id, dist, prev):
        self.id = id
        self.prev = prev
        self.dist = dist
    
    def __str__(self):
        return '(id:%s prev:%s dist:%s)' % (self.id, self.prev, self.dist)


class UnsortedListPriorityQueue(PriorityQueue):
    def __init__(self):
        self.list = {}

    def makeQueue(self, nodes):
        # Returns the initial list of vertices entered into the queue
        queue = []
        for node in nodes:
            self.insert(PriorityQueueEntry(node.node_id, float('inf'), None))
            queue.append(self.list[node.node_id])
        return queue

    def insert(self, entry):
        self.list[entry.id] = entry

    def deleteMin(self):
        # Search for the minimum value still in the queue
        min = next(iter(self.list))
        min_entry = self.list[min]
        for k in self.list.keys():
            entry = self.list[k]
            if min_entry.dist > entry.dist:
                min = k
                min_entry = entry
        del self.list[min]
        return min_entry

    def decreaseKey(self, changed):
        # Nothing to update except the node value
        self.list[changed.id].dist = changed.dist
        self.list[changed.id].prev = changed.prev


class BinaryMinHeapPriorityQueue(PriorityQueue):   
    def makeQueue(self, nodes):
        # Returns the initial list of vertices entered into the queue
        queue = []
        for node in nodes:
            self.insert(PriorityQueueEntry(node.node_id, float('inf'), None))
            queue.append(self.list[node.node_id])
        return queue

    def insert(self, entry):
        idx = len(self.list)
        self.list.append(entry)

        # Update map to enable constant lookup
        self.list_idx[entry.id] = idx
        self.bubbleUp(idx)

    def deleteMin(self):
        min = PriorityQueueEntry(self.list[0].id,
                                 self.list[0].dist,
                                 self.list[0].prev)
        # Swap minimum with leaf in heap, bubble down to right priority
        back = len(self.list) - 1
        self.swap(0, back)
        del self.list[back]
        self.bubbleDown(0)
        return min

    def decreaseKey(self, changed):
        idx = self.list_idx.get(changed.id)
        self.list[idx] = changed
        self.bubbleUp(idx)

    def swap(self, parent, child):
        # Swaps two nodes
        temp = self.list[parent]
        parent_id = temp.id
        child_id = self.list[child].id
        self.list[parent] = self.list[child]
        self.list[child] = temp
        self.list_idx[parent_id] = child
        self.list_idx[child_id] = parent

    def bubbleUp(self, child):
        # The parent of any child (assuming starting at index 1) is child // 2.
        parent = (child + 1)//2 - 1
        if parent >= 0 and self.list[parent].dist > self.list[child].dist:
            self.swap(parent, child)
            # Check for continuing to bubble up
            self.bubbleUp(parent)

    def bubbleDown(self, parent):
        # The child of any node (assuming starting at index 1) is parent * 2.
        child = parent * 2 + 1

        # Get smaller of two children
        if (len(self.list) > (child + 1) and
            self.list[child + 1].dist < self.list[child].dist):
            child += 1
        
        if (len(self.list) > child and
            self.list[parent].dist > self.list[child].dist):
            self.swap(parent, child)
            # Check for continuing to bubble down 
            self.bubbleDown(child)


class NetworkRoutingSolver:
    def __init__( self ):
        pass

    def initializeNetwork( self, network ):
        assert( type(network) == CS312Graph )
        self.network = network

    def getShortestPath( self, destIndex ):
        self.dest = destIndex

        path_edges = []
        node = self.shortest_paths[self.dest]
        
        changed = True
        while node.id != node.prev and node.prev is not None and changed:
            changed = False
            for edge in self.network.nodes[node.prev].neighbors:
                if node.id == edge.dest.node_id:
                    path_edges.append((edge.src.loc, edge.dest.loc, '{:.0f}'.format(edge.length)))
                    node = self.shortest_paths[node.prev]
                    changed = True
                    break
            
        total_length = self.shortest_paths[self.dest].dist
        return {'cost':total_length, 'path':path_edges}

    def dijkstra(self, use_heap):
        shortest_paths = {}
        queue = UnsortedListPriorityQueue()
        if use_heap:
            queue = BinaryMinHeapPriorityQueue()
        shortest_paths = queue.makeQueue(self.network.nodes)
        start = PriorityQueueEntry(self.source, 0, self.source)
        queue.decreaseKey(start)
        
        while not queue.empty():
            next = queue.deleteMin()
            shortest_paths[next.id] = next

            for edge in self.network.nodes[next.id].neighbors:
                id = edge.dest.node_id
                if next.dist + edge.length < shortest_paths[id].dist:
                    shortest_paths[id].dist = next.dist + edge.length
                    shortest_paths[id].prev = next.id
                    queue.decreaseKey(shortest_paths[id])

        return shortest_paths

    def computeShortestPaths( self, srcIndex, use_heap=False ):
        self.source = srcIndex
        t1 = time.time()

        self.shortest_paths = self.dijkstra(use_heap)

        t2 = time.time()
        return (t2-t1)

