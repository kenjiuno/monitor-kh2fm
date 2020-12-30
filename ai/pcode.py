# FEDCBA9876 54 3210
# ----- opc typ pushOp
# 0000000000 00 0000 u32: PUSH.V ri
# Note: the order is reversed in table: 0000 00 0000000000.

ArgPart3 = 1
Arg16 = 16
Arg16_2 = 32
Arg32 = 64
Syscall = 256
Gosub = 512
UnconditionalBranch = 1024
ConditionalBranch = 2048
NeverReturn = 4096
GosubRet = 8192

table = [
    # push
    [0, 0, None, "PUSH.L0 u32 ", "pushImm", Arg32],
    [0, 1, None, "PUSH.L1 u32 ", "pushImm", Arg32],
    [0, 2, 0, "PUSH.L +sp", "pushFromPSp", Arg16],
    [0, 2, 1, "PUSH.L +wp", "pushFromPWp",  Arg16],
    [0, 2, 2, "PUSH.L +(*sp)", "pushFromPSpVal", Arg16],
    [0, 2, 3, "PUSH.L *2 +top", "pushFromPAi", Arg16],
    [0, 3, 0, "PUSH.AP +sp", "pushFromFSp", Arg16],
    [0, 3, 1, "PUSH.AP +wp", "pushFromFWp", Arg16],
    [0, 3, 2, "PUSH.AP +(*sp)", "pushFromFSpVal", Arg16],
    [0, 3, 3, "PUSH.AP *2 +top", "pushFromFAi", Arg16],
    # pop
    [1, None, 0, "POP.L +sp", "popToSp", Arg16],
    [1, None, 1, "POP.L +wp", "popToWp", Arg16],
    [1, None, 2, "POP.L +(*sp)", "popToSpVal", Arg16],
    [1, None, 3, "POP.L *2 +top", "popToAi", Arg16],
    # 2 unk
    [2, None, 0, "?", "memcpyToSp", Arg16 | Arg16_2],
    [2, None, 1, "?", "memcpyToWp", Arg16 | Arg16_2],
    [2, None, 2, "?", "memcpyToSpVal", Arg16 | Arg16_2],
    [2, None, 3, "?", "memcpyToSpAi", Arg16 | Arg16_2],
    # 3 unk
    [3, None, None, "?", "fetchValue", Arg16],
    # 4 unk
    [4, None, None, "?", "memcpy", Arg16],
    # unary int
    [5, 0, 0, "CFTI", "cfti", 0],
    [5, 0, 2, "NEG", "neg", 0],
    [5, 0, 3, "INV", "inv", 0],
    [5, 0, 4, "EQZ", "eqz", 0],
    [5, 0, 5, "ABS", "abs", 0],
    [5, 0, 6, "MSB", "msb", 0],
    [5, 0, 7, "INFO", "info", 0],
    [5, 0, 8, "EQZ", "eqz", 0],
    [5, 0, 9, "NEQZ", "neqz", 0],
    [5, 0, 10, "MSBI", "msbi", 0],
    [5, 0, 11, "IPOS", "ipos", 0],
    # unary float
    [5, 1, 1, "CITF", "citf", 0],
    [5, 1, 2, "NEGF", "negf", 0],
    [5, 1, 5, "ABSF", "absf", 0],
    [5, 1, 6, "INFZF", "infzf", 0],
    [5, 1, 7, "INFOEZF", "infoezf", 0],
    [5, 1, 8, "EQZF", "eqzf", 0],
    [5, 1, 9, "NEQZF", "neqzf", 0],
    [5, 1, 10, "SUPOEZF", "supoezf", 0],
    [5, 1, 11, "SUPZF", "supzf", 0],
    # binary int
    [6, 0, 0, "ADD", "add", 0],
    [6, 0, 1, "SUB", "sub", 0],
    [6, 0, 2, "MUL", "mul", 0],
    [6, 0, 3, "DIV", "div", 0],
    [6, 0, 4, "MOD", "mod", 0],
    [6, 0, 5, "AND", "and", 0],
    [6, 0, 6, "OR", "or", 0],
    [6, 0, 7, "XOR", "xor", 0],
    [6, 0, 8, "SLL", "sll", 0],
    [6, 0, 9, "SRA", "sra", 0],
    [6, 0, 10, "EQZV", "eqzv", 0],
    [6, 0, 11, "NEQZV", "neqzv", 0],
    # binary float
    [6, 1, 0, "ADDF", "addf", 0],
    [6, 1, 1, "SUBF", "subf", 0],
    [6, 1, 2, "MULF", "mulf", 0],
    [6, 1, 3, "DIVF", "divf", 0],
    [6, 1, 4, "MODF", "modf", 0],
    # branch
    [7, 0, 0, "J", "j",  UnconditionalBranch | Arg16],
    [7, 0, 1, "JNZ", "jnz",  ConditionalBranch | Arg16],
    [7, 0, 2, "JZ", "jz",  ConditionalBranch | Arg16],
    # gosub
    [8, None, None, "GOSUB", "gosub", Gosub | ArgPart3 | Arg16],
    # other
    [9, None, 0, "EXIT", "halt", 0],
    [9, None, 1, "?", "exit", NeverReturn],
    [9, None, 2, "RET", "ret", GosubRet],
    [9, None, 3, "PUSH.CA", "drop", 0],
    [9, None, 5, "PUSH.C", "dup", 0],
    [9, None, 6, "SIN", "sin", 0],
    [9, None, 7, "COS", "cos", 0],
    [9, None, 8, "DEGR", "degr", 0],
    [9, None, 9, "RADD", "radd", 0],
    # syscall
    [10, None, None, "SYSCALL", "syscall", Syscall | Arg16],
    # 11 unk
    [11, 0, 0, "?", "gosub32", Gosub | ArgPart3 | Arg32],
]
