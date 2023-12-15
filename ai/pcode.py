from typing import List, Optional

# FEDCBA9876 54 3210
# ----- opc typ pushOp
# 0000000000 00 0000 u32: PUSH.V ri
# Note: the order is reversed in table: 0000 00 0000000000.

ArgSsub = 1
Arg16 = 2
Arg32 = 4
NextRelative = 8
AiPos = 16
WorkPos = 32
Float32 = 64

Syscall = 256
Gosub = 512
Jump = 1024
Conditional = 2048
NeverReturn = 4096
GosubRet = 8192


class OpArg:
    name: str
    flags: int

    def __init__(self, name, flags):
        self.name = name
        self.flags = flags


class OpDef:
    opc: int
    sub: Optional[int]
    ssub: Optional[int]
    name: str
    behavior: int
    args: List[OpArg]
    oldnames: List[str]

    def __init__(
        self,
        opc: int,
        sub: Optional[int],
        ssub: Optional[int],
        org: str,
        name: str,
        behavior: int,
        args: List[OpArg],
        oldnames: List[str],
    ):
        self.opc = opc
        self.sub = sub
        self.ssub = ssub
        self.name = name
        self.behavior = behavior
        self.args = args
        self.oldnames = oldnames


table: List[OpDef] = [
    # push
    OpDef(0, 0, None, "PUSH.L0 u32 ", "push", 0, [OpArg("imm32", Arg32)], ["pushImm"]),
    OpDef(
        0,
        1,
        None,
        "PUSH.L1 u32 ",
        "push.s",
        0,
        [OpArg("float32", Float32)],
        ["pushImmf"],
    ),
    OpDef(
        0, 2, 0, "PUSH.L +sp", "push.sp", 0, [OpArg("imm16", Arg16)], ["pushFromPSp"]
    ),
    OpDef(
        0,
        2,
        1,
        "PUSH.L +wp",
        "push.wp",
        0,
        [OpArg("imm16", Arg16 | WorkPos)],
        ["pushFromPWp"],
    ),
    OpDef(
        0,
        2,
        2,
        "PUSH.L +(*sp)",
        "push.tp",
        0,
        [OpArg("imm16", Arg16)],
        ["pushFromPSpVal"],
    ),
    OpDef(
        0,
        2,
        3,
        "PUSH.L *2 +top",
        "push.text",
        0,
        [OpArg("imm16", Arg16 | AiPos)],
        ["pushFromPAi"],
    ),
    OpDef(
        0, 3, 0, "PUSH.AP +sp", "push.f.sp", 0, [OpArg("imm16", Arg16)], ["pushFromFSp"]
    ),
    OpDef(
        0,
        3,
        1,
        "PUSH.AP +wp",
        "push.f.wp",
        0,
        [OpArg("imm16", Arg16 | WorkPos)],
        ["pushFromFWp"],
    ),
    OpDef(
        0,
        3,
        2,
        "PUSH.AP +(*sp)",
        "push.f.tp",
        0,
        [OpArg("imm16", Arg16)],
        ["pushFromFSpVal"],
    ),
    OpDef(
        0,
        3,
        3,
        "PUSH.AP *2 +top",
        "push.f.text",
        0,
        [OpArg("imm16", Arg16 | AiPos)],
        ["pushFromFAi"],
    ),
    # pop
    OpDef(1, None, 0, "POP.L +sp", "pop.sp", 0, [OpArg("imm16", Arg16)], ["popToSp"]),
    OpDef(
        1,
        None,
        1,
        "POP.L +wp",
        "pop.wp",
        0,
        [OpArg("imm16", Arg16 | WorkPos)],
        ["popToWp"],
    ),
    OpDef(
        1, None, 2, "POP.L +(*sp)", "pop.tp", 0, [OpArg("imm16", Arg16)], ["popToSpVal"]
    ),
    OpDef(
        1,
        None,
        3,
        "POP.L *2 +top",
        "pop.text",
        0,
        [OpArg("imm16", Arg16 | AiPos)],
        ["popToAi"],
    ),
    # 2 memcpyTo
    OpDef(
        2,
        None,
        0,
        "?",
        "memcpy.sp",
        0,
        [OpArg("imm16", Arg16), OpArg("imm16_2", Arg16)],
        ["memcpyToSp"],
    ),
    OpDef(
        2,
        None,
        1,
        "?",
        "memcpy.wp",
        0,
        [OpArg("imm16", Arg16), OpArg("imm16_2", Arg16 | WorkPos)],
        ["memcpyToWp"],
    ),
    OpDef(
        2,
        None,
        2,
        "?",
        "memcpy.tp",
        0,
        [OpArg("imm16", Arg16), OpArg("imm16_2", Arg16)],
        ["memcpyToSpVal"],
    ),
    OpDef(
        2,
        None,
        3,
        "?",
        "memcpy.text",
        0,
        [OpArg("imm16", Arg16), OpArg("imm16_2", Arg16 | AiPos)],
        ["memcpyToSpAi"],
    ),
    # 3 fetch
    OpDef(3, None, None, "?", "fetch", 0, [OpArg("imm16", Arg16)], ["fetchValue"]),
    # 4 memcpyGeneric
    OpDef(4, None, None, "?", "memcpy", 0, [OpArg("ssub", ArgSsub)], []),
    # unary op (integer)
    OpDef(5, 0, 0, "CITF", "cvt.w.s", 0, [], ["citf"]),
    OpDef(5, 0, 2, "NEG", "neg", 0, [], []),
    OpDef(5, 0, 3, "INV", "not", 0, [], ["inv"]),
    OpDef(5, 0, 4, "EQZ", "seqz", 0, [], ["eqz"]),
    OpDef(5, 0, 5, "ABS", "abs", 0, [], []),
    OpDef(5, 0, 6, "MSB", "sltz", 0, [], ["msb"]),
    OpDef(5, 0, 7, "INFO", "slez", 0, [], ["info"]),
    OpDef(5, 0, 8, "EQZ", "seqz", 0, [], ["eqz"]),
    OpDef(5, 0, 9, "NEQZ", "snez", 0, [], ["neqz"]),
    OpDef(5, 0, 10, "MSBI", "sgez", 0, [], ["msbi"]),
    OpDef(5, 0, 11, "IPOS", "sgtz", 0, [], ["ipos"]),
    # unary op (floating-point)
    OpDef(5, 1, 1, "CFTI", "cvt.s.w", 0, [], ["cfti"]),
    OpDef(5, 1, 2, "NEGF", "neg.s", 0, [], ["negf"]),
    OpDef(5, 1, 5, "ABSF", "abs.s", 0, [], ["absf"]),
    OpDef(5, 1, 6, "INFZF", "sltz.s", 0, [], ["infzf"]),
    OpDef(5, 1, 7, "INFOEZF", "slez.s", 0, [], ["infoezf"]),
    OpDef(5, 1, 8, "EQZF", "seqz.s", 0, [], ["eqzf"]),
    OpDef(5, 1, 9, "NEQZF", "snez.s", 0, [], ["neqzf"]),
    OpDef(5, 1, 10, "SUPOEZF", "sgez.s", 0, [], ["supoezf"]),
    OpDef(5, 1, 11, "SUPZF", "sgtz.s", 0, [], ["supzf"]),
    # binary op (integer)
    OpDef(6, 0, 0, "ADD", "add", 0, [], []),
    OpDef(6, 0, 1, "SUB", "sub", 0, [], []),
    OpDef(6, 0, 2, "MUL", "mul", 0, [], []),
    OpDef(6, 0, 3, "DIV", "div", 0, [], []),
    OpDef(6, 0, 4, "MOD", "mod", 0, [], []),
    OpDef(6, 0, 5, "AND", "and", 0, [], []),
    OpDef(6, 0, 6, "OR", "or", 0, [], []),
    OpDef(6, 0, 7, "XOR", "xor", 0, [], []),
    OpDef(6, 0, 8, "SLL", "sll", 0, [], []),
    OpDef(6, 0, 9, "SRA", "sra", 0, [], []),
    OpDef(6, 0, 10, "EQZV", "land", 0, [], ["eqzv"]),
    OpDef(6, 0, 11, "NEQZV", "lor", 0, [], ["neqzv"]),
    # binary op (floating-point)
    OpDef(6, 1, 0, "ADDF", "add.s", 0, [], ["addf"]),
    OpDef(6, 1, 1, "SUBF", "sub.s", 0, [], ["subf"]),
    OpDef(6, 1, 2, "MULF", "mul.s", 0, [], ["mulf"]),
    OpDef(6, 1, 3, "DIVF", "div.s", 0, [], ["divf"]),
    OpDef(6, 1, 4, "MODF", "mod.s", 0, [], ["modf"]),
    # branch
    OpDef(7, None, 0, "J", "b", Jump, [OpArg("imm16", Arg16 | NextRelative)], ["jmp"]),
    OpDef(
        7,
        None,
        1,
        "JZ",
        "beqz",
        Conditional | Jump,
        [OpArg("imm16", Arg16 | NextRelative)],
        ["jz"],
    ),
    OpDef(
        7,
        None,
        2,
        "JNZ",
        "bnez",
        Conditional | Jump,
        [OpArg("imm16", Arg16 | NextRelative)],
        ["jnz"],
    ),
    # gosub
    OpDef(
        8,
        None,
        None,
        "GOSUB",
        "jal",
        Gosub,
        [OpArg("ssub", ArgSsub), OpArg("imm16", Arg16 | NextRelative)],
        ["gosub"],
    ),
    # other
    OpDef(9, None, 0, "EXIT", "halt", 0, [], []),
    OpDef(9, None, 1, "?", "exit", NeverReturn, [], []),
    OpDef(9, None, 2, "RET", "ret", GosubRet, [], []),
    OpDef(9, None, 3, "PUSH.CA", "drop", 0, [], []),
    OpDef(9, None, 5, "PUSH.C", "dup", 0, [], []),
    OpDef(9, None, 6, "SIN", "sin", 0, [], []),
    OpDef(9, None, 7, "COS", "cos", 0, [], []),
    OpDef(9, None, 8, "DEGR", "degr", 0, [], []),
    OpDef(9, None, 9, "RADD", "radd", 0, [], []),
    # syscall
    OpDef(
        10,
        None,
        None,
        "SYSCALL",
        "syscall",
        Syscall,
        [OpArg("ssub", ArgSsub), OpArg("imm16", Arg16)],
        [],
    ),
    # 11 gosub32
    OpDef(
        11,
        None,
        None,
        "?",
        "jal32",
        Gosub,
        [OpArg("ssub", ArgSsub), OpArg("imm32", Arg32 | NextRelative)],
        ["gosub32"],
    ),
]
