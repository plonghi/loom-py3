import numpy
import sympy
#import logging
import warnings
from fractions import Fraction
from sympy import limit, oo
from cmath import log


class LocalDiffError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class GetSWallSeedsError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class NNearestError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class UnravelError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def ctor2(complex_number):
    return (complex_number.real, complex_number.imag)


def r2toc(real_tuple):
    return (real_tuple[0]+1j*real_tuple[1])


def get_root_multiplicity(coefficients, root_0, accuracy):
    """
    Returns the multiplicity of a root of a polynomial
    defined by the list 'coefficients' according to numpy.roots
    """
    multiplicity = 0
    roots = numpy.roots(coefficients)
    for root_i in roots:
        if abs(root_0 - root_i) < accuracy:
            multiplicity += 1

    return multiplicity


def cpow(base, exponent_numerator, exponent_denominator=1):
    return complex(base)**complex(Fraction(exponent_numerator,
                                           exponent_denominator))

def gather(a_list, compare):
    """
    Gather elements of the given list
        [a_0, b_0, a_1, c_0, b_1]
    into a dict
        {a_0: [a_0, a_1], b_0: [b_0, b_1], c_0: [c_0]},
    where compare(a_0, a_1) == True, compare(a_0, b_0) == False, etc.
    """
    if len(a_list) == 0:
        return {}
    group = {}
    e_0 = a_list[0]
    group[e_0] = [e_0]
    for e in a_list[1:]:
        for key in group.keys():
            if compare(key, e) is True:
                group[key].append(e)
                break
        else:
            group[e] = [e]
    return group


def remove_duplicate(a_list, compare):
    return gather(a_list, compare).keys()


def n_remove_duplicate(a_list, accuracy):
    compare = lambda a, b: abs(a - b) < accuracy
    return gather(a_list, compare).keys()


def n_nearest(a_list, value, n):
    """
    Find n elements of a_list nearest to value and return them,
    by comparing the euclidean norms.
    """
    compare = lambda v1, v2: cmp(abs(v1 - value), abs(v2 - value))
    return sorted(a_list, cmp=compare)[:n]


def n_nearest_indices(a_list, value, n):
    """
    Find n elements of a_list nearest to value and return their indices,
    by comparing the euclidean norms.
    """
    compare = lambda v1, v2: cmp(abs(v1 - value), abs(v2 - value))
    key = lambda k: a_list[k]
    sorted_indices = sorted(range(len(a_list)), cmp=compare, key=key)
    return sorted_indices[:n]


def unravel(k, row_size, column_size=None):
    """
    return unflattened indices of a matrix.
    """
    if column_size is None:
        column_size = row_size

    if k < 0:
        error_msg = 'k = {} should not be negative.'.format(k)
        raise UnravelError(error_msg)

    i = k / row_size
    j = k % row_size

    if i > column_size:
        error_msg = ('i = {} should not be greater than '
                     'the size of the column = {}.'.format(i, column_size))
        raise UnravelError(error_msg)

    return (i, j)


def PSL2C(C, z, inverse=False, numerical=False):
    """
    Apply linear fractional transformation defined by C onto z.
    """
    if C is None:
        C = [[1, 0], [0, 1]]

    if inverse is True:
        a = C[1][1]
        b = -C[0][1]
        c = -C[1][0]
        d = C[0][0]
    else:
        a = C[0][0]
        b = C[0][1]
        c = C[1][0]
        d = C[1][1]

    if numerical is True:
        numer = complex(a) * complex(z) + complex(b)
        denom = complex(c) * complex(z) + complex(d)
        return numer/denom
    else:
        u = sympy.symbols('u')
        Cu = (a*u+b)/(c*u+d)

        if z == oo:
            Cz = limit(Cu, u, z)
        else:
            Cz = Cu.subs(u, z)

        return Cz


def put_on_cylinder(z, mt_params=None):
    """
    Put PSL2C-transformed z-coords
    onto the original cylinder.
    """
    return log(PSL2C(mt_params, z, inverse=True, numerical=True))/1.0j


### chan: TODO: use numba?
def delete_duplicates(l, key=None, accuracy=False):
    seen = set()
    uniq = []
    if key==None and accuracy==None:
        for x in l:
            if not isinstance(x, (int, bool, str, unicode)):
                warnings.warn('delete_duplicates(): testing the membership'
                              'of an element of an unsupported type.')
            if x not in seen:
                uniq.append(x)
                seen.add(x)
    elif key==None and accuracy != None:
        uniq = n_remove_duplicate(l, accuracy)

    elif key!=None and accuracy == None:
        for x in l:
            if key(x) not in seen:
                uniq.append(x)
                seen.add(key(x))
    else:
        for x in l:
            if (
                len(n_remove_duplicate(list(seen) + [key(x)], accuracy)) 
                > len(seen)
            ):
                uniq.append(x)
                seen.add(key(x))
            
    return uniq


def parse_sym_dict_str(string):
    """
    Get a string of the form
        {k_str: v_str, ...}
    or
        {k_str = v_str, ...}
    and return a list of
        [(k_str, v_str), ...]
    """
    result = []
    for k_v_str in string.lstrip('{').rstrip('}').split(','):
        item = k_v_str.split(':')
        if len(item) != 2:
            item = k_v_str.split('=')
        if len(item) != 2:
            raise SyntaxError('Require {var = val,} or {var : val,}.')
        k_str, v_str = item
        result.append((k_str.strip(), v_str.strip()))
    return result


def is_root(np_array, g_data):
    ans = False
    for rt in list(g_data.roots):
        if (np_array == rt).all():
            ans = True
            break
        else:
            pass
    return ans


def get_descendant_roots(p1_roots, p2_roots, g_data):
    descendant_roots = []
    old_roots = p1_roots
    new_roots = p2_roots
    while len(new_roots) > 1:
        root_buffer = []
        for old_root in old_roots:
            for new_root in new_roots:
                root_sum = old_root + new_root
                if is_root(root_sum, g_data):
                    root_buffer.append(root_sum)
        descendant_roots += root_buffer
        old_roots += new_roots
        new_roots = root_buffer


def get_turning_points(zs):
    """
    Return a list of indices of turning points of a curve on the z-plane,
    i.e. dx/dy = 0 or dy/dx = 0, where x = z[t].real and y = z[t].imag.
    """
    tps = []

    if len(zs) < 3:
        return tps

    x_0 = zs[0].real
    y_0 = zs[0].imag

    for t in range(1, len(zs) - 1):
        x_1 = zs[t].real
        y_1 = zs[t].imag
        x_2 = zs[t + 1].real
        y_2 = zs[t + 1].imag
        if (
            (x_1 - x_0) * (x_2 - x_1) < 0 or (y_1 - y_0) * (y_2 - y_1) < 0
        ): 
            tps.append(t)
        x_0 = x_1
        y_0 = y_1
    return tps


def get_splits_with_overlap(splits):
    """
    Get the start & the end indicies of a list according to the splits.

    When the given split is [i_0, i_1, ...], this returns
    [
        [0, i_0 + 1],
        [i_0, i_1 + 1],
        ...
    ]
    """
    new_splits = []
    start = 0
    for split in splits:
        stop = split + 1
        new_splits.append((start, stop))
        start = split
    new_splits.append((start, None))
    return new_splits


