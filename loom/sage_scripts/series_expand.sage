# script for series expansion of a multivariable expression
# arguments should be as follows: 
# expression, list of variables, list of expansion points, list of expansion degrees
# Example: in terminal write
#        sage series_expand.sage '(1+x+y)**2' 'x, y' '[0.0, I]' '[2,2]'
# this will return
#       (2*x + 2*I + 2)*(y - I) + (2*I + 2)*x + 2*I
#
# WARNING !!! : do NOT pass variables as '[x, y]' but always as 'x, y'

import sys
import pdb

expr_str = sys.argv[1]
var_names = var(sys.argv[2])
var_x0 = eval(sys.argv[3])
var_deg = eval(sys.argv[4])

# if the variables are many, var_names is a list like (x, y)
# but with a single variable it just gives x, no list
# so here we fix this and make a list of a single variable too
if len(var_names) > 1:
    n_vars = len(var_names)
else:
    var_names = [var_names]
    n_vars = 1

series_exp = eval(expr_str)

for n in range(0, n_vars):
    x_n = var(var_names[n])
    series_exp = series_exp.series(x_n==var_x0[n], var_deg[n]).truncate()

print series_exp
