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

# io_pairs = [
#     ((2, 3, 12, 1), 156),
#     ((0, 14, 3, 11), 196),
#     ((4, 1, 6, 1), 112),
#     ((0, 7, 13, 2), 105),
#     ((1, 2, 13, 1), 56),
#     ((4, 2, 7, 1), 256),
#     ((4, 10, 12, 1), 2080),
#     ((1, 1, 4, 9), 26),
#     ((3, 3, 3, 9), 288),
#     ((4, 14, 5, 3), 1792),
# ]

def test(pairs):
    # MANUALLY REPLACE THE "a + b + c + d" WITH A PYTHON EXPRESSION
    # CORRESPONDING TO YOUR ANSWER FROM Z3. If its correct, the test will print
    # 'Your program satisfies all IO pairs!'
    def program(a, b, c, d):
        return (((a * b) | d) << c) & 0xFFFF

    sat = True
    for (a, b, c, d), o in pairs:
        sat = sat and (program(a, b, c, d) == o & 0xFFFF)

    if sat:
        print('Your program satisfies all IO pairs!')
    else:
        print('Your program does not satisfy the IO pairs')


if __name__ == '__main__':
    test(io_pairs)
