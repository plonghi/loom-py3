"""
A general intersection module.

Objects and functions to find intersections of real 1-dim curves
on a real 2-dim plane.
"""

import logging
import numpy
# import pdb

from scipy.interpolate import interp1d
from scipy.optimize import brentq, newton
from sympy import Interval
from itertools import combinations


class NoIntersection(Exception):
    """
    An exception class to be raised when failed
    to find an intersection.
    """
    def __init__(self, value=''):
        self.value = value

    def __str__(self):
        return repr(self.value)


def remove_duplicate_intersection(new_ilist, old_ilist):
    """
    Remove any duplicate in new_ilist1, then remove intersections
    of new_ilist that already exist in old_ilist
    """
    temp_ilist = new_ilist

    for intersection1, intersection2 in combinations(temp_ilist, 2):
        if intersection1 == intersection2:
            new_ilist.remove(intersection2)
        else:
            continue

    temp_ilist = new_ilist

    for new_intersection in temp_ilist:
        for intersection in old_ilist:
            if new_intersection == intersection:
                new_ilist.remove(new_intersection)


# def find_curve_range_intersection(curve_1, curve_2, cut_at_inflection=False):
#     """
#     Return intersections of x- and y-ranges of two real curves,
#     which are parametric curves on the xy-plane given as
#     (x_array, y_array), a tuple of NumPy arrays.
#     """
#     x1, y1 = curve_1
#     x2, y2 = curve_2

#     if cut_at_inflection is True:
#         x1_min, x1_max = sorted([x1[0], x1[-1]])
#         x2_min, x2_max = sorted([x2[0], x2[-1]])

#         y1_min, y1_max = sorted([y1[0], y1[-1]])
#         y2_min, y2_max = sorted([y2[0], y2[-1]])
#     else:
#         x1_min, x1_max = numpy.sort(x1)[[0, -1]]
#         x2_min, x2_max = numpy.sort(x2)[[0, -1]]

#         y1_min, y1_max = numpy.sort(y1)[[0, -1]]
#         y2_min, y2_max = numpy.sort(y2)[[0, -1]]

#     x1_interval = Interval(x1_min, x1_max)
#     x2_interval = Interval(x2_min, x2_max)

#     y1_interval = Interval(y1_min, y1_max)
#     y2_interval = Interval(y2_min, y2_max)

#     x_range = x1_interval.intersect(x2_interval)
#     y_range = y1_interval.intersect(y2_interval)

#     return [x_range, y_range]


def find_single_intersection(
    z_list_1, z_list_2, int_threshold=0.03,
    ):
    """
    Takes two lists of points in the complex plane, and
    finds a single pair of points from list 1 and from list 2
    that are closest to each other, and within a distance
    from each other |z_1 - z_2| < int_radius.
    This function returns a list of proper times and the single 
    intersection point
    [t1, t2, z_int]
    corresponding to the positions of the closest points, and to the 
    estimated actual intersection.
    """
    closest_pt = [0, 0, abs(z_list_1[0] - z_list_2[0])]
    for t1 in list(range(len(z_list_1))):
        for t2 in list(range(len(z_list_2))):
            delta = abs(z_list_1[t1] - z_list_2[t2])
            if delta < closest_pt[2]:
                closest_pt = [t1, t2, delta]

    if closest_pt[2] < int_threshold:
        # now we have the times t1 and t2 where the two trajectories
        # are closest to each other.
        # Next we find two consdecutive points on the 1st trajectory
        # and on the second one, such that the segments connecting
        # them should intersect very close to the actual intersection point

        t1 = closest_pt[0]
        t2 = closest_pt[1]

        if t1 == (len(z_list_1) - 1):
            z1_i , z1_f =  [z_list_1[t1 - 1], z_list_1[t1]]

        elif t1 == 0:
            z1_i , z1_f =  [z_list_1[t1], z_list_1[t1 + 1]]

        else:
            if (
                abs(z_list_1[t1 + 1] -z_list_2[t2]) < 
                abs(z_list_1[t1 - 1] -z_list_2[t2])
            ):
                z1_i, z1_f = [z_list_1[t1], z_list_1[t1 + 1]]
            else:
                z1_i, z1_f = [z_list_1[t1 - 1], z_list_1[t1]]

        if t2 == (len(z_list_2) - 1):
            z2_i , z2_f =  [z_list_2[t2 - 1], z_list_2[t2]]

        elif t2 == 0:
            z2_i , z2_f =  [z_list_2[t2], z_list_2[t2 + 1]]

        else:
            if (
                abs(z_list_2[t2 + 1] -z_list_1[t1]) < 
                abs(z_list_2[t2 - 1] -z_list_1[t1])
            ):
                z2_i, z2_f = [z_list_2[t2], z_list_2[t2 + 1]]
            else:
                z2_i, z2_f = [z_list_2[t2 - 1], z_list_2[t2]]

        # now consider the linear system of equations 
        # for the intersection of two lines 
        # y = a1 x + b1
        # y = a2 x + b2
        # where
        # a1 = Im(z1_f - z1_i) / Re(z1_f - z1_i)
        # b1 = Im(z1_i) - Re(z1_i) * a1
        # and similarly for a2, b2.
        # The intersection point is then at
        # z = z_r + z_i
        # with
        # z_r = (b2 - b1) / (a1 - a2)
        # z_i = (a1 * b2 - a2 * b1) / (a1 - a2)

        a1 = numpy.imag(z1_f - z1_i) / numpy.real(z1_f - z1_i)
        b1 = numpy.imag(z1_i) - numpy.real(z1_i) * a1
        a2 = numpy.imag(z2_f - z2_i) / numpy.real(z2_f - z2_i)
        b2 = numpy.imag(z2_i) - numpy.real(z2_i) * a2

        z_int_r = (b2 - b1) / (a1 - a2)
        z_int_i = (a1 * b2 - a2 * b1) / (a1 - a2)
        z_int = z_int_r + 1j * z_int_i

        return [t1, t2, z_int]

    else:
        return []




### The following is a method based on clustering of intersections -- now deprecated
### but may be useful in the future

def k_means(data, k=1, normalize=False, limit=500):
    """Basic k-means clustering algorithm.
    """
    # optionally normalize the data. k-means will perform poorly or strangely if the dimensions
    # don't have the same ranges.
    if normalize:
        stats = (data.mean(axis=0), data.std(axis=0))
        data = (data - stats[0]) / stats[1]
    
    # pick the first k points to be the centers. this also ensures that each group has at least
    # one point.
    centers = data[:k]

    for i in range(limit):
        # core of clustering algorithm...
        # first, use broadcasting to calculate the distance from each point to each center, then
        # classify based on the minimum distance.
        classifications = numpy.argmin(((data[:, :, None] - centers.T[None, :, :])**2).sum(axis=1), axis=1)
        # next, calculate the new centers for each cluster.
        new_centers = numpy.array([data[classifications == j, :].mean(axis=0) for j in range(k)])

        # if the centers aren't moving anymore it is time to stop.
        if (new_centers == centers).all():
            break
        else:
            centers = new_centers
    else:
        # this will not execute if the for loop exits on a break.
        raise RuntimeError(f"Clustering algorithm did not complete within {limit} iterations")
            
    # if data was normalized, the cluster group centers are no longer scaled the same way the original
    # data is scaled.
    if normalize:
        centers = centers * stats[1] + stats[0]

    return classifications, centers

# TO DO: consider dynamical definition of search_radius
# to take into account if two trajectories have widely-spaced
# data points, then ther intersection may be missed.
def find_potential_intersection(
    z_list_1, z_list_2, int_threshold=0.03, search_radius=0.2,
    ):
    """
    Takes two lists of points in the complex plane, and
    finds a single pair of points from list 1 and from list 2
    that are closest to each other, and within a distance
    from each other |z_1 - z_2| < int_radius.
    This function returns a list of proper times and intersection points
    [[t1, t2, z_12], ...]
    corresponding to the positions of the closest points, and to the 
    estimated actual intersection.
    """
    closest_pts = []
    for t1 in list(range(len(z_list_1))):
        for t2 in list(range(len(z_list_2))):
            if abs(z_list_1[t1] - z_list_2[t2]) < search_radius:
                closest_pts.append([t1, t2, z_list_1[t1], z_list_2[t2]])
    
    if len(closest_pts) > 0:
        classification, centers = k_means(
            numpy.array(closest_pts), k=1, normalize=True,
        )
        # we only look for a single center (intersection)
        [t1_int, t2_int, z1_int, z2_int] = centers[0]
        if abs(z1_int - z2_int) < int_threshold:
            return [
                t1_int.real, 
                t2_int.real, 
                0.5 * (z1_int + z2_int)
                ]
        else:
            return []
    else:
        return []


def unit_tan_vec(z_list, t):
    """
    compute the unit tangent vactor of a 
    trajectory given as a list of points in the
    complex plane, at time t
    """
    if numpy.floor(t) == 0:
        i_0 = 0
        i_1 = 1
    elif numpy.ceil(t) == len(z_list) - 1:
        i_0 = len(z_list) - 2
        i_2 = len(z_list) - 1
    else:
        i_0 = numpy.floor(t)
        i_1 = numpy.ceil(t)
        
    return numpy.array(
        [(z_list[1] - z_list[0]).real, (z_list[1] - z_list[0]).imag]
    )

def are_parallel(z_list_1, z_list_2, t_1, t_2, tangency_threshold=0.01,):
    """
    determine whether two trajectories have parallel or 
    anti-parallel tangents at given points parametrized
    by proper times t_1 and t_2
    """
    v1 = unit_tan_vec(z_list_1, t_1)
    v2 = unit_tan_vec(z_list_2, t_2)
    
    return (
        numpy.linalg.norm(v1 + v2) < tangency_threshold or
        numpy.linalg.norm(v1 - v2) < tangency_threshold
    )

def determine_intersection_point(
    z_list_1, z_list_2, #accuracy,
):
    """
    Find a single interection between two trajectories.
    This function assumes that there is only one intersection.
    """
    # TO DO: generalize to handle multiple intersections, using
    # the function find_potential_intersections
    # with an arbitrary number of clusters
    
    # potential_intersection = find_potential_intersection(
    #     z_list_1, z_list_2, #int_threshold=accuracy
    # )
    potential_intersection = find_single_intersection(
        z_list_1, z_list_2, #int_threshold=accuracy
    )
    if len(potential_intersection) > 0:
        [t1, t2, z_int] = potential_intersection
        if are_parallel(z_list_1, z_list_2, t1, t2) == False:
            return potential_intersection
        else:
            return []
    else:
        return []

### DEPRECATED
# def find_intersection_of_segments(segment_1, segment_2, accuracy=1e-1,
#                                   newton_maxiter=5):
#     """
#     Find an intersection of two segments of curves.

#     First find interpolations of segments using scipy.interp1d and
#     use SciPy's Brent method to find an intersection. When this
#     doesn't work, use SciPy's polynomial interpolation and then use
#     secant method to find an intersection.

#     Parameters
#     ----------
#     segment_1, segment_2: Segments to find their intersection. Each
#         segment is (x_array, y_array), a tuple of NumPy arrays.
#     newton_maxiter: Maximum number of iterations for secant method.
#         When increased, this gives a better accuracy of the
#         intersection but it also greatly reduces the performance
#         due to many cases when there is no intersection but
#         the module keeps trying to find one.
#     """
#     # First ccheck if either of the segments is empty
#     if (segment_1[0].size==0 or segment_1[1].size==0 or
#         segment_2[0].size==0 or segment_2[1].size==0):
#         raise NoIntersection()
#     # First check if the two segments share any x- and y-range.
#     x_range, y_range = find_curve_range_intersection(
#         segment_1, segment_2, cut_at_inflection=True
#     )
#     print('The x_range and y_range for searching intersections are\n{}\nand\n{}'.format(x_range, y_range))
#     if (x_range.is_EmptySet or y_range.is_EmptySet or x_range.is_FiniteSet or
#             y_range.is_FiniteSet):
#         # The segments and the bin do not share a domain and therefore
#         # there is no intersection.
#         raise NoIntersection()

#     f1 = interp1d(*segment_1)
#     f2 = interp1d(*segment_2)
#     delta_f12 = lambda x: f1(x) - f2(x)

#     try:
#         logging.debug('try brentq.')
#         intersection_x = brentq(delta_f12, x_range.start, x_range.end)
#         intersection_y = f1(intersection_x)
#         print('find_intersection_of_segments with brentq')

#     except ValueError:
#         print('cannot find_intersection_of_segments with brentq')
#         x0 = 0.5 * (x_range.start + x_range.end)

#         try:
#             logging.debug('try newton with x0 = %.8f.', x0)
#             intersection_x = newton(delta_f12, x0, maxiter=newton_maxiter)
#             logging.debug('intersection_x = %.8f.', intersection_x)
#             print('intersection_x with newton = {}.'.format(intersection_x))
            
#         except ValueError:
#             print('got ValueError')
#             # newton() searches for x outside the interpolation domain.
#             # Declare no intersection.
#             raise NoIntersection()
#         except RuntimeError:
#             print('got RuntimeError')
#             # Newton's method fails to converge; declare no intersection
#             raise NoIntersection()

#         # Verify the solution returned by newton().
#         if abs(delta_f12(intersection_x)) > accuracy:
#             print('intersection is beyond accuracy')
#             raise NoIntersection()

#         # Check if the intersection is within the curve range.
#         # If not, the intersecion is not valid.
#         if intersection_x not in x_range:
#             print('intersection is beyond x_range')
#             raise NoIntersection()
#         intersection_y = f1(intersection_x)
#         if intersection_y not in y_range:
#             print('intersection is beyond y_range')
#             raise NoIntersection()

#     return [float(intersection_x), float(intersection_y)]
