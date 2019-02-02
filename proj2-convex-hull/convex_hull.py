# this is 4-5 seconds slower on 1000000 points than Ryan's desktop...  Why?


from PyQt5.QtCore import QLineF, QPointF, QThread, pyqtSignal



import time

def slope(a, b):
    delta_x = b.x() - a.x()
    delta_y = b.y() - a.y()
    return delta_y / delta_x


class ConvexHull():
    def __init__(self, top, bottom):
        self.top = top
        self.bottom = bottom
    
    def __str__(self):
        return 'top: %s\nbottom: %s' % (self.top, self.bottom)


def mergeHulls(left, right):
    # Merge top
    tl = -1
    tr = 0
    l_min = 0 - len(left.top)
    r_max = len(right.top) - 1
    did_pivot = True
    cur_slope = slope(left.top[tl], right.top[tr])
    while did_pivot:
        did_pivot = False        
        while tr < r_max and slope(left.top[tl], right.top[tr+1]) > cur_slope:
            tr += 1
            cur_slope = slope(left.top[tl], right.top[tr])
            did_pivot = True
        
        while tl > l_min and slope(left.top[tl-1], right.top[tr]) < cur_slope:
            tl -= 1
            cur_slope = slope(left.top[tl], right.top[tr])
            did_pivot = True

    tl += len(left.top) + 1
    top = left.top[:tl] + right.top[tr:]
    
    # Merge bottom: same as top except mirrored
    bl = 0
    br = -1
    l_max = len(left.bottom) - 1
    r_min = 0 - len(right.bottom)
    did_pivot = True
    cur_slope = slope(left.bottom[bl], right.bottom[br])

    while did_pivot:
        did_pivot = False
        while br > r_min and slope(left.bottom[bl], right.bottom[(br-1)]) < cur_slope:
            br -= 1
            cur_slope = slope(left.bottom[bl], right.bottom[br])
            did_pivot = True
        
        while bl < l_max and slope(left.bottom[bl+1], right.bottom[br]) > cur_slope:
            bl += 1
            cur_slope = slope(left.bottom[bl], right.bottom[br])
            did_pivot = True

    br += len(right.bottom) + 1
    bottom = right.bottom[:br] + left.bottom[bl:]


    result = ConvexHull(top, bottom)
    return result

def solveConvexHull(points):
    if len(points) <= 3:
        top = []
        top.append(points[0])
        bottom = []
        bottom.insert(0, points[0])

        for p in points[1:-1]:
            if p.y() > points[0].y():
                top.append(p)
            elif p.y() < points[0].y():
                bottom.insert(0,p)

        top.append(points[-1])
        bottom.insert(0, points[-1])

        return ConvexHull(top, bottom)

    else:
        half = len(points)//2
        left = solveConvexHull(points[:half])
        right = solveConvexHull(points[half:])
        return mergeHulls(left, right)

class ConvexHullSolverThread(QThread):
    def __init__(self, unsorted_points,demo):
        self.points = unsorted_points                    
        self.pause = demo
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    # These two signals are used for interacting with the GUI.
    show_hull    = pyqtSignal(list,tuple)
    display_text = pyqtSignal(str)

    # Some additional thread signals you can implement and use for debugging,
    # if you like
    show_tangent = pyqtSignal(list,tuple)
    erase_hull = pyqtSignal(list)
    erase_tangent = pyqtSignal(list)
                    

    def set_points( self, unsorted_points, demo):
        self.points = unsorted_points
        self.demo   = demo


    def run(self):
        assert( type(self.points) == list and type(self.points[0]) == QPointF )

        n = len(self.points)
        print( 'Computing Hull for set of {} points'.format(n) )

        t1 = time.time()
        self.points = sorted(self.points, key=lambda k: [k.x(), k.y()])
        t2 = time.time()
        print('Time Elapsed (Sorting): {:3.3f} sec'.format(t2-t1))

        t3 = time.time()
        convex_hull = solveConvexHull(self.points)
        t4 = time.time()

        USE_DUMMY = False
        if USE_DUMMY:
            # This is a dummy polygon of the first 3 unsorted points
            polygon = [QLineF(self.points[i],self.points[(i+1)%3]) for i in range(3)]
            
            # When passing lines to the display, pass a list of QLineF objects.
            # Each QLineF object can be created with two QPointF objects
            # corresponding to the endpoints
            assert( type(polygon) == list and type(polygon[0]) == QLineF )

            # Send a signal to the GUI thread with the hull and its color
            self.show_hull.emit(polygon,(0,255,0))

        else:
            # TODO: PASS THE CONVEX HULL LINES BACK TO THE GUI FOR DISPLAY
            polygon = []
            t_size = len(convex_hull.top)
            for i in range(t_size-1):
                line = QLineF(convex_hull.top[i], convex_hull.top[(i+1)%t_size])
                polygon.append(line)
            
            b_size = len(convex_hull.bottom)
            for i in range(b_size-1):
                line = QLineF(convex_hull.bottom[i], convex_hull.bottom[(i+1)%b_size])
                polygon.append(line)

            assert( type(polygon) == list and type(polygon[0]) == QLineF )

            self.show_hull.emit(polygon,(0,255,0)) 

            
        # Send a signal to the GUI thread with the time used to compute the 
        # hull
        self.display_text.emit('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))
        print('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))
            

