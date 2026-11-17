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

# position of operator (1st, 2nd, 3rd) and two different inputs
def op(n, x1, x2):
    return mul(4*n, x1, x2)+lor(4*n+1, x1, x2)+shl(4*n+2, x1, x2)+add(4*n+3, x1, x2)

def shapes(x0, x1, x2, x3):
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

    # three operation slot each take one operator out of four
    for ops in range(3):
        constraints.append(exactly_one_flag([4*ops+i for i in range(4)]))

    # inputs flags 12-36 (24 permutation of orderings)
    # only one of those permutation is correct
    constraints.append(exactly_one_flag(range(12,36)))

    # paranthesis shape should be one of five combination
    constraints.append(exactly_one_flag(range(36,41)))

    for i, (inputs, output) in enumerate(pairs):
        a,b,c,d = [BitVecVal(v,16) for v in inputs]

        options = []
        # go through constraint 12~36 for inputs
        for j, (x0, x1, x2, x3) in enumerate(permutations([a,b,c,d])):
            # go through constraint 36~41 for all parenthesis combination
            for k, tree in enumerate(shapes(x0, x1, x2, x3)):
                options.append(And(Bool(f'B{12+j}'), Bool(f'B{36+k}'), tree == output))
        constraints.append(Or(options))

    return And(constraints)

def decoder(ans):
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

    # chose shape
    for i in range(5):
        if is_true(ans[Bool(f'B{i+36}')]):
            expr = shapes[i]
            break

    # choose input
    for i in range(24):
        if is_true(ans[Bool(f'B{i+12}')]):
            order = input_perm[i]
            break

    for i in range(4):
        expr = expr.replace(f'x{i}', order[i])

    # choose operator
    for i in range(3):
        for j in range(4):
            if is_true(ans[Bool(f'B{4*i+j}')]):
                op = ops[j]
                break
        expr = expr.replace(f'op{i}', op)

    return expr


if __name__ == '__main__':
    s = formula(io_pairs)
    print(f'Z3 formula: {s}')
    print('Z3 Solution:')
    solver = Solver()
    solver.add(s)
    if solver.check() == sat:
        answer = solver.model()
        print(answer)
        print(f'answer: {decoder(answer)}')
    else:
        print('no solution')