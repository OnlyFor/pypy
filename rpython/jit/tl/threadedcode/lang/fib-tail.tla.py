from rpython.jit.tl.threadedcode import tla

code = [
    tla.CONST_INT, 0, 
    tla.CONST_INT, 1, 
    tla.CONST_N, 0, 1, 134, 160, 
    tla.DUPN, 2, 
    tla.DUPN, 2, 
    tla.DUPN, 2, 
    tla.CALL_ASSEMBLER, 25, 3, 
    tla.DUP, 
    tla.PRINT, 
    tla.POP1, 
    tla.POP1, 
    tla.POP1, 
    tla.POP1, 
    tla.EXIT, 
    tla.DUPN, 1, 
    tla.CONST_INT, 1, 
    tla.GT, 
    tla.JUMP_IF, 36, 
    tla.DUPN, 3, 
    tla.JUMP, 71, 
    tla.DUPN, 1, 
    tla.CONST_INT, 2, 
    tla.GT, 
    tla.JUMP_IF, 47, 
    tla.DUPN, 2, 
    tla.JUMP, 71, 
    tla.DUPN, 3, 
    tla.DUPN, 3, 
    tla.ADD, 
    tla.DUPN, 2, 
    tla.CONST_INT, 1, 
    tla.SUB, 
    tla.DUPN, 4, 
    tla.DUPN, 2, 
    tla.DUPN, 2, 
    tla.FRAME_RESET, 3, 2, 3, 
    tla.JUMP, 25, 
    tla.POP1, 
    tla.POP1, 
    tla.RET, 3, 
]