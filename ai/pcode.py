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
CodeRevealerLabeling = 16384


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
    desc: str

    def __init__(
        self,
        opc: int,
        sub: Optional[int],
        ssub: Optional[int],
        desc: str,
        name: str,
        behavior: int,
        args: List[OpArg],
        oldnames: List[str],
    ):
        self.opc = opc
        self.sub = sub
        self.ssub = ssub
        self.desc = desc
        self.name = name
        self.behavior = behavior
        self.args = args
        self.oldnames = oldnames


table: List[OpDef] = [
    # push
    OpDef(
        0,
        0,
        None,
        "`push           int32`",
        "push",
        CodeRevealerLabeling,
        [OpArg("imm32", Arg32)],
        ["pushImm"],
    ),
    OpDef(
        0,
        1,
        None,
        "`push           single`",
        "push.s",
        0,
        [OpArg("float32", Float32)],
        ["pushImmf"],
    ),
    OpDef(
        0,
        2,
        0,
        "`push           sp     + int16`",
        "push.sp",
        0,
        [OpArg("imm16", Arg16)],
        ["pushFromPSp"],
    ),
    OpDef(
        0,
        2,
        1,
        "`push           wp     + int16`",
        "push.wp",
        0,
        [OpArg("imm16", Arg16 | WorkPos)],
        ["pushFromPWp"],
    ),
    OpDef(
        0,
        2,
        2,
        "`push          *sp     + int16`",
        "push.sp.d",
        0,
        [OpArg("imm16", Arg16)],
        ["pushFromPSpVal"],
    ),
    OpDef(
        0,
        2,
        3,
        "`push           bd     + int16`",
        "push.bd",
        0,
        [OpArg("imm16", Arg16 | AiPos)],
        ["pushFromPAi"],
    ),
    OpDef(
        0,
        3,
        0,
        "`push        *( sp     + int16)`",
        "push.d.sp",
        0,
        [OpArg("imm16", Arg16)],
        ["pushFromFSp"],
    ),
    OpDef(
        0,
        3,
        1,
        "`push        *( wp     + int16)`",
        "push.d.wp",
        0,
        [OpArg("imm16", Arg16 | WorkPos)],
        ["pushFromFWp"],
    ),
    OpDef(
        0,
        3,
        2,
        "`push        *(*sp     + int16)`",
        "push.d.sp.d",
        0,
        [OpArg("imm16", Arg16)],
        ["pushFromFSpVal"],
    ),
    OpDef(
        0,
        3,
        3,
        "`push        *( bd     + int16)`",
        "push.d.bd",
        0,
        [OpArg("imm16", Arg16 | AiPos)],
        ["pushFromFAi"],
    ),
    # pop
    OpDef(
        1,
        None,
        0,
        "`pop         *( sp     + int16)`",
        "pop.sp",
        0,
        [OpArg("imm16", Arg16)],
        ["popToSp"],
    ),
    OpDef(
        1,
        None,
        1,
        "`pop         *( wp     + int16)`",
        "pop.wp",
        0,
        [OpArg("imm16", Arg16 | WorkPos)],
        ["popToWp"],
    ),
    OpDef(
        1,
        None,
        2,
        "`pop         *(*sp     + int16)`",
        "pop.sp.d",
        0,
        [OpArg("imm16", Arg16)],
        ["popToSpVal"],
    ),
    OpDef(
        1,
        None,
        3,
        "`pop         *( bd     + int16)`",
        "pop.bd",
        0,
        [OpArg("imm16", Arg16 | AiPos)],
        ["popToAi"],
    ),
    # 2 memcpyTo
    OpDef(
        2,
        None,
        0,
        "`memcpy to    ( sp     + int16)`",
        "memcpy.sp",
        0,
        [OpArg("imm16", Arg16), OpArg("imm16_2", Arg16)],
        ["memcpyToSp"],
    ),
    OpDef(
        2,
        None,
        1,
        "`memcpy to    ( wp     + int16)`",
        "memcpy.wp",
        0,
        [OpArg("imm16", Arg16), OpArg("imm16_2", Arg16 | WorkPos)],
        ["memcpyToWp"],
    ),
    OpDef(
        2,
        None,
        2,
        "`memcpy to    (*sp     + int16)`",
        "memcpy.sp.d",
        0,
        [OpArg("imm16", Arg16), OpArg("imm16_2", Arg16)],
        ["memcpyToSpVal"],
    ),
    OpDef(
        2,
        None,
        3,
        "`memcpy to    ( bd     + int16)`",
        "memcpy.bd",
        0,
        [OpArg("imm16", Arg16), OpArg("imm16_2", Arg16 | AiPos)],
        ["memcpyToSpAi"],
    ),
    # 3 fetch
    OpDef(
        3,
        None,
        None,
        "`push        *( pop()  + int16)`",
        "push.d.pop",
        0,
        [OpArg("imm16", Arg16)],
        ["fetchValue"],
    ),
    # 4 memcpyGeneric
    OpDef(4, None, None, "generic memcpy", "memcpy", 0, [OpArg("ssub", ArgSsub)], []),
    # unary op (integer)
    OpDef(5, 0, 0, "int to float (convert word to single)", "cvt.w.s", 0, [], ["citf"]),
    OpDef(5, 0, 2, "1 to -1, -1 to 1", "neg", 0, [], []),
    OpDef(5, 0, 3, "bitwise not", "not", 0, [], ["inv"]),
    OpDef(5, 0, 4, "set 1 if: equal to 0", "seqz", 0, [], ["eqz"]),
    OpDef(5, 0, 5, "get absolute integer (negative to positive)", "abs", 0, [], []),
    OpDef(5, 0, 6, "set 1 if: less than 0 (negative)", "sltz", 0, [], ["msb"]),
    OpDef(
        5,
        0,
        7,
        "set 1 if: less or equal to 0 (negative and zero)",
        "slez",
        0,
        [],
        ["info"],
    ),
    OpDef(5, 0, 8, "set 1 if: equal to 0", "seqz", 0, [], ["eqz"]),
    OpDef(5, 0, 9, "set 1 if: not equal to 0", "snez", 0, [], ["neqz"]),
    OpDef(
        5,
        0,
        10,
        "set 1 if: greater or equal to 0 (zero and positive)",
        "sgez",
        0,
        [],
        ["msbi"],
    ),
    OpDef(5, 0, 11, "set 1 if: greater than 0 (positive)", "sgtz", 0, [], ["ipos"]),
    # unary op (floating-point)
    OpDef(5, 1, 1, "float to int (convert single to word)", "cvt.s.w", 0, [], ["cfti"]),
    OpDef(5, 1, 2, "1.0 to -1.0, -1.0 to 1.0", "neg.s", 0, [], ["negf"]),
    OpDef(
        5, 1, 5, "get absolute float (negative to positive)", "abs.s", 0, [], ["absf"]
    ),
    OpDef(5, 1, 6, "set 1 if: less than 0 (negative)", "sltz.s", 0, [], ["infzf"]),
    OpDef(
        5,
        1,
        7,
        "set 1 if: less or equal to 0 (negative and zero)",
        "slez.s",
        0,
        [],
        ["infoezf"],
    ),
    OpDef(5, 1, 8, "set 1 if: equal to 0", "seqz.s", 0, [], ["eqzf"]),
    OpDef(5, 1, 9, "set 1 if: not equal to 0", "snez.s", 0, [], ["neqzf"]),
    OpDef(
        5,
        1,
        10,
        "set 1 if: greater or equal to 0 (zero and positive)",
        "sgez.s",
        0,
        [],
        ["supoezf"],
    ),
    OpDef(5, 1, 11, "set 1 if: greater than 0 (positive)", "sgtz.s", 0, [], ["supzf"]),
    # binary op (integer)
    OpDef(6, 0, 0, "`push a; push b; (a + b)`", "add", 0, [], []),
    OpDef(6, 0, 1, "`push a; push b; (a - b)`", "sub", 0, [], []),
    OpDef(6, 0, 2, "`push a; push b; (a * b)`", "mul", 0, [], []),
    OpDef(6, 0, 3, "`push a; push b; (a / b)`", "div", 0, [], []),
    OpDef(6, 0, 4, "`push a; push b; (a % b)`", "mod", 0, [], []),
    OpDef(6, 0, 5, "Bitwise and", "and", 0, [], []),
    OpDef(6, 0, 6, "Bitwise or", "or", 0, [], []),
    OpDef(6, 0, 7, "Bitwise xor", "xor", 0, [], []),
    OpDef(6, 0, 8, "Shift left logical (unsigned)", "sll", 0, [], []),
    OpDef(6, 0, 9, "Shift right arithmetic (signed)", "sra", 0, [], []),
    OpDef(6, 0, 10, "`push a; push b; (a && b)`", "land", 0, [], ["eqzv"]),
    OpDef(6, 0, 11, "`push a; push b; (a || b)`", "lor", 0, [], ["neqzv"]),
    # binary op (floating-point)
    OpDef(6, 1, 0, "`push a; push b; (a + b)` float", "add.s", 0, [], ["addf"]),
    OpDef(6, 1, 1, "`push a; push b; (a - b)` float", "sub.s", 0, [], ["subf"]),
    OpDef(6, 1, 2, "`push a; push b; (a * b)` float", "mul.s", 0, [], ["mulf"]),
    OpDef(6, 1, 3, "`push a; push b; (a + b)` float", "div.s", 0, [], ["divf"]),
    OpDef(6, 1, 4, "`push a; push b; (a % b)` float", "mod.s", 0, [], ["modf"]),
    # branch
    OpDef(
        7,
        None,
        0,
        "branch unconditionally",
        "b",
        Jump,
        [OpArg("imm16", Arg16 | NextRelative)],
        ["jmp"],
    ),
    OpDef(
        7,
        None,
        1,
        "branch if zero",
        "beqz",
        Conditional | Jump,
        [OpArg("imm16", Arg16 | NextRelative)],
        ["jz"],
    ),
    OpDef(
        7,
        None,
        2,
        "branch if non-zero",
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
        "local function call (16-bit address)",
        "jal",
        Gosub,
        [OpArg("ssub", ArgSsub), OpArg("imm16", Arg16 | NextRelative)],
        ["gosub"],
    ),
    # other
    OpDef(9, None, 0, "halt", "halt", 0, [], []),
    OpDef(9, None, 1, "exit", "exit", NeverReturn, [], []),
    OpDef(9, None, 2, "ret", "ret", GosubRet, [], []),
    OpDef(9, None, 3, "drop one value from `tp`", "drop", 0, [], []),
    OpDef(9, None, 5, "duplicate one value at `tp`", "dup", 0, [], []),
    OpDef(9, None, 6, "sin", "sin", 0, [], []),
    OpDef(9, None, 7, "cos", "cos", 0, [], []),
    OpDef(9, None, 8, "radian to degree: `value / PI * 180.0`", "degr", 0, [], []),
    OpDef(9, None, 9, "degree to radian: `value / 180.0 * PI`", "radd", 0, [], []),
    # syscall
    OpDef(
        10,
        None,
        None,
        "syscall",
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
        "local function call (32-bit address)",
        "jal32",
        Gosub,
        [OpArg("ssub", ArgSsub), OpArg("imm32", Arg32 | NextRelative)],
        ["gosub32"],
    ),
]
