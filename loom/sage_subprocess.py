# Force integer division to give a float, i.e. 1/2 = 0.5.
from __future__ import division
from sympy import sympify, poly
from mpmath import mp, mpc
import logging
import os
import subprocess
# import pdb

base_dir = os.path.dirname(os.path.realpath(__file__))
sage_script_dir = base_dir + '/sage_scripts/'
sage_bin_path = '/usr/bin/sage'


def solve_system_of_eqs(eqs, precision=None, logger_name='loom',):
    """
    Use sage to solve the given system of polynomial equations of x and z.
    """
    logger = logging.getLogger(logger_name)
    sols = []
    if precision is not None:
        mp.dps = precision
    else:
        precision = 15
    logger.info(
        'Use SAGE to solve {} @ precision = {}.'.format(eqs, precision)
    )
    try:
        rv_str = subprocess.check_output(
            [sage_bin_path, sage_script_dir + 'solve_system_of_eqs.sage'] +
            [str(precision)] +
            [str(eq) for eq in eqs]
        ).decode("utf-8")
    except (KeyboardInterrupt, SystemExit):
        raise

    rv = eval(rv_str)
    sols_str_list, messages = rv

    for msg in messages:
        logger.warning(msg)

    for sols_str in sols_str_list:
        (z_re, z_im), (x_re, x_im) = sols_str
        sols.append(
            (mpc(z_re, z_im), mpc(x_re, x_im))
        )

    return sols


def solve_single_eq_single_var(
    eq, var=None, precision=None, logger_name='loom',
):
    """
    Use sage to solve a single polynomial equation in a single variable.
    """
    logger = logging.getLogger(logger_name)
    sols = []
    if precision is not None:
        mp.dps = precision
    else:
        precision = 15

    if var is None:
        raise Exception('Must specify variable for solving the equation.')
    else:
        try:
            rv_str = subprocess.check_output(
                [sage_bin_path, sage_script_dir + 
                    'solve_single_eq_single_var.sage'] +
                [str(precision), str(eq), var]
            ).decode("utf-8")
        except (KeyboardInterrupt, SystemExit):
            raise

    rv = eval(rv_str)
    sols_str_list, mult_str_list, messages = rv

    for msg in messages:
        logger.warning(msg)

    for i, sols_str in enumerate(sols_str_list):
        (z_re, z_im) = sols_str
        for j in range(mult_str_list[i]):
            sols.append(
                mpc(z_re, z_im)
            )

    return sols


def get_g_data(root_system, highest_weight):
    try:
        g_data_str = subprocess.check_output(
            [sage_bin_path, sage_script_dir + 'get_g_data.sage', root_system,
             str(highest_weight)]
        )
    except (KeyboardInterrupt, SystemExit):
        raise

    g_data = eval(g_data_str)

    return g_data


def compute_discriminant(f):
    """
    Use SAGE to compute the discriminant of a polynomial f.
    f must be expressed in variables x, z.
    The discriminant will be computed with respect to x.
    """
    try:
        disc_str = subprocess.check_output(
            [sage_bin_path, sage_script_dir + 'compute_discriminant.sage'] +
            [str(f)]
        ).decode("utf-8")
    except (KeyboardInterrupt, SystemExit):
        raise
    disc_sym = sympify(disc_str)
    if disc_sym == 0:
        return 0
    else:
        return poly(disc_sym)

def series_expand(
        expression, vars_list, x0_list, degrees_list, logger_name='loom',
    ):
    """
    Use sage to compute a multivariate series expansion.
    arguments should be as follows: 
    expression, list of variables, list of expansion points, list of expansion 
    degrees. 
    Example: in terminal one would write
        sage series_expand.sage '(1+x+y)**2' 'x, y' '[0.0, I]' '[2,2]'
    this will return
        (2*x + 2*I + 2)*(y - I) + (2*I + 2)*x + 2*I
    """
    logger = logging.getLogger(logger_name)

    # for the variable list, we turn it into a string like '[x, y]'
    # we then remove the brackets from the string (this is necessary 
    # formatting for the sage script, see there), to yield 'x, y'
    try:
        ans_str = subprocess.check_output(
            [sage_bin_path, sage_script_dir + 'series_expand.sage',
            str(expression),
            str(vars_list)[1:-1],
            str(x0_list),
            str(degrees_list)]
        ).decode("utf-8")
    except (KeyboardInterrupt, SystemExit):
        raise

    return ans_str  