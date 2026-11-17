from z3 import *
from itertools import *

# IO Pairs:
#   IN: (11, 6, 9, 4)    OUT:  35840
#   IN: (9, 12, 10, 1)   OUT:  46080
#   IN: (2, 4, 0, 4)     OUT:     12
#   IN: (14, 8, 10, 3)   OUT:  52224
#   IN: (1, 13, 9, 4)    OUT:   6656
#   IN: (4, 2, 8, 0)     OUT:   2048
#   IN: (15, 6, 12, 4)   OUT:  57344
#   IN: (7, 12, 6, 0)    OUT:   5376
#   IN: (2, 0, 6, 0)     OUT:      0
#   IN: (16, 4, 3, 1)    OUT:    520

io_pairs = [
    ((11, 6, 9, 4), 35840),
    ((9, 12, 10, 1), 46080),
    ((2, 4, 0, 4), 12),
    ((14, 8, 10, 3), 52224),
    ((1, 13, 9, 4), 6656),
    ((4, 2, 8, 0), 2048),
    ((15, 6, 12, 4), 57344),
    ((7, 12, 6, 0), 5376),
    ((2, 0, 6, 0), 0),
    ((16, 4, 3, 1), 520),
]

# Convenience functions for creating a constraint using a flag with identifier
# 'i' that toggles whether the operator is used for operands x1 and x2.
# Use is OPTIONAL.
def mul(i, x1, x2):
    return If(Bool(f'B{i}'), x1 * x2, BitVecVal(0,16))

def lor(i, x1, x2):
    return If(Bool(f'B{i}'), x1 | x2, BitVecVal(0,16))

def shl(i, x1, x2):
    return If(Bool(f'B{i}'), x1 << x2, BitVecVal(0,16))

def add(i, x1, x2):
    return If(Bool(f'B{i}'), x1 + x2, BitVecVal(0,16))

# if only one of constraint is true, then true
def exactly_one_flag(nums):
   return Sum([If(Bool(f'B{i}'), 1, 0) for i in nums]) == 1

# possible choices to make
ops = ['*', '|', '<<', '+']
input_perm = list(permutations(['a', 'b', 'c', 'd']))
shapes = [
    # ((x0 0th x1) 1st x2) 2nd x3
    '((x0 op0 x1) op1 x2) op2 x3',
    # (x0 0th (x1 1st x2)) 2nd x3
    '(x0 op0 (x1 op1 x2)) op2 x3',
    # (x0 0th x1) 1st (x2 2nd x3)
    '(x0 op0 x1) op1 (x2 op2 x3)',
    # x0 0th ((x1 1st x2) 2nd x3)
    'x0 op0 ((x1 op1 x2) op2 x3)',
    # x0 0th (x1 1st (x2 2nd x3))
    'x0 op0 (x1 op1 (x2 op2 x3))'
]

# choices that solver make
ops_chosen = [Int('op0'), Int('op1'), Int('op2')]
input_perm_chosen = Int('input_perm')
shape_chosen = Int('shapes')

# position of operator (1st, 2nd, 3rd) and two different inputs
def op(n, x1, x2):
    c = ops_chosen[n]
    return If(c == 0, x1*x2,
            If (c == 1, x1 | x2,
                If (c==2, x1<<x2, 
                        x1+x2)))

def trees(x0, x1, x2, x3):
    return [
        # ((x0 0th x1) 1st x2) 2nd x3
        op(2, op(1, op(0, x0, x1), x2), x3),
        # (x0 0th (x1 1st x2)) 2nd x3
        op(2, op(0, x0, op(1, x1, x2)), x3),
        # (x0 0th x1) 1st (x2 2nd x3)
        op(1, op(0, x0, x1), op(2, x2, x3)),
        # x0 0th ((x1 1st x2) 2nd x3)
        op(0, x0, op(2, op(1, x1, x2), x3)),
        # x0 0th (x1 1st (x2 2nd x3))
        op(0, x0, op(1, x1, op(2, x2, x3))),
    ]

# Your Synthesizer: construct a Z3 formula using input/output pairs.
def formula(pairs):
    constraints = []

    # one choice for each must be in valid index of choice
    for c in ops_chosen:
        constraints.append(And(0<= c, c<len(ops)))
    constraints.append(And(0<= input_perm_chosen, input_perm_chosen<len(input_perm)))
    constraints.append(And(0<=shape_chosen, shape_chosen<len(shapes)))

    # permute through each input and output, ordering.
    for i, (inputs, output) in enumerate(pairs):
        # map input to variable
        val = dict(zip(['a','b', 'c', 'd'], inputs))
        # try various ordering
        for j, order in enumerate(input_perm):
            x = [BitVecVal(val[name], 16) for name in order]
            # try various parenthesis shape 
            for k, tree in enumerate(trees(*x)):
                constraints.append(Implies(And(input_perm_chosen==j, shape_chosen==k), tree == output))

    return And(constraints)

if __name__ == '__main__':
    s = formula(io_pairs)
    print(f'Z3 formula: {s}')
    print('Z3 Solution:')
    solve(s)