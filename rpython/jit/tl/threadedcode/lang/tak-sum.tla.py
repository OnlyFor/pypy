from rpython.jit.tl.threadedcode import tla

code = [
    tla.CONST_INT, 12,
    tla.CONST_INT, 5,
    tla.CONST_INT, 0,
    tla.DUPN, 2,
    tla.DUPN, 2,
    tla.DUPN, 2,
    tla.CALL, 56, 3,
    tla.PRINT,
    tla.POP1,
    tla.POP1,
    tla.POP1,
    tla.POP1,
    tla.EXIT,
    tla.DUPN, 2,
    tla.CONST_INT, 1,
    tla.GT,
    tla.JUMP_IF, 32,
    tla.DUPN, 1,
    tla.JUMP, 54,
    tla.DUPN, 2,
    tla.CONST_INT, 1,
    tla.SUB,
    tla.DUPN, 2,
    tla.DUPN, 4,
    tla.ADD,
    tla.DUPN, 1,
    tla.DUPN, 1,
    tla.FRAME_RESET, 2, 2, 2,
    tla.JUMP, 21,
    tla.POP1,
    tla.POP1,
    tla.RET, 2,
    tla.DUPN, 3,
    tla.CONST_INT, 1,
    tla.SUB,
    tla.DUPN, 3,
    tla.DUPN, 1,
    tla.LT,
    tla.JUMP_IF, 86,
    tla.CONST_N, 0, 0, 39, 16,
    tla.CONST_INT, 0,
    tla.DUPN, 1,
    tla.DUPN, 1,
    tla.CALL, 21, 2,
    tla.POP1,
    tla.POP1,
    tla.JUMP, 143,
    tla.DUPN, 4,
    tla.CONST_INT, 1,
    tla.SUB,
    tla.DUP,
    tla.DUPN, 5,
    tla.DUPN, 5,
    tla.CALL, 56, 3,
    tla.DUPN, 5,
    tla.CONST_INT, 1,
    tla.SUB,
    tla.DUP,
    tla.DUPN, 6,
    tla.DUPN, 9,
    tla.CALL, 56, 3,
    tla.DUPN, 6,
    tla.CONST_INT, 1,
    tla.SUB,
    tla.DUP,
    tla.DUPN, 10,
    tla.DUPN, 10,
    tla.CALL, 56, 3,
    tla.DUPN, 4,
    tla.DUPN, 3,
    tla.DUPN, 2,
    tla.FRAME_RESET, 3, 7, 3,
    tla.JUMP, 56,
    tla.POP1,
    tla.POP1,
    tla.POP1,
    tla.POP1,
    tla.POP1,
    tla.POP1,
    tla.POP1,
    tla.RET, 3,
]
