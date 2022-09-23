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

    def __init__(self, opc: int, sub: Optional[int], ssub: Optional[int], org: str, name: str, behavior: int, args: List[OpArg]):
        self.opc = opc
        self.sub = sub
        self.ssub = ssub
        self.name = name
        self.behavior = behavior
        self.args = args


table: List[OpDef] = [
    # push
    OpDef(0, 0, None, "PUSH.L0 u32 ", "pushImm", 0, [OpArg('imm32', Arg32)]),
    OpDef(0, 1, None, "PUSH.L1 u32 ", "pushImm", 0, [OpArg('imm32', Arg32)]),
    OpDef(0, 2, 0, "PUSH.L +sp", "pushFromPSp", 0, [OpArg('imm16', Arg16)]),
    OpDef(0, 2, 1, "PUSH.L +wp", "pushFromPWp", 0, [OpArg('imm16', Arg16)]),
    OpDef(0, 2, 2, "PUSH.L +(*sp)", "pushFromPSpVal",
          0, [OpArg('imm16', Arg16)]),
    OpDef(0, 2, 3, "PUSH.L *2 +top", "pushFromPAi",
          0, [OpArg('imm16', Arg16 | AiPos)]),
    OpDef(0, 3, 0, "PUSH.AP +sp", "pushFromFSp", 0, [OpArg('imm16', Arg16)]),
    OpDef(0, 3, 1, "PUSH.AP +wp", "pushFromFWp", 0, [OpArg('imm16', Arg16)]),
    OpDef(0, 3, 2, "PUSH.AP +(*sp)", "pushFromFSpVal",
          0, [OpArg('imm16', Arg16)]),
    OpDef(0, 3, 3, "PUSH.AP *2 +top", "pushFromFAi",
          0, [OpArg('imm16', Arg16 | AiPos)]),
    # pop
    OpDef(1, None, 0, "POP.L +sp", "popToSp", 0, [OpArg('imm16', Arg16)]),
    OpDef(1, None, 1, "POP.L +wp", "popToWp", 0, [OpArg('imm16', Arg16)]),
    OpDef(1, None, 2, "POP.L +(*sp)", "popToSpVal",
          0, [OpArg('imm16', Arg16)]),
    OpDef(1, None, 3, "POP.L *2 +top", "popToAi",
          0, [OpArg('imm16', Arg16 | AiPos)]),
    # 2 unk
    OpDef(2, None, 0, "?", "memcpyToSp", 0, [
          OpArg('imm16', Arg16), OpArg('imm16_2', Arg16)]),
    OpDef(2, None, 1, "?", "memcpyToWp", 0, [
          OpArg('imm16', Arg16), OpArg('imm16_2', Arg16)]),
    OpDef(2, None, 2, "?", "memcpyToSpVal", 0, [
          OpArg('imm16', Arg16), OpArg('imm16_2', Arg16)]),
    OpDef(2, None, 3, "?", "memcpyToSpAi", 0, [
          OpArg('imm16', Arg16), OpArg('imm16_2', Arg16 | AiPos)]),
    # 3 unk
    OpDef(3, None, None, "?", "fetchValue", 0, [OpArg('imm16', Arg16)]),
    # 4 unk
    OpDef(4, None, None, "?", "memcpy", 0, [OpArg('ssub', ArgSsub)]),
    # unary int
    OpDef(5, 0, 0, "CFTI", "cfti", 0, []),
    OpDef(5, 0, 2, "NEG", "neg", 0, []),
    OpDef(5, 0, 3, "INV", "inv", 0, []),
    OpDef(5, 0, 4, "EQZ", "eqz", 0, []),
    OpDef(5, 0, 5, "ABS", "abs", 0, []),
    OpDef(5, 0, 6, "MSB", "msb", 0, []),
    OpDef(5, 0, 7, "INFO", "info", 0, []),
    OpDef(5, 0, 8, "EQZ", "eqz", 0, []),
    OpDef(5, 0, 9, "NEQZ", "neqz", 0, []),
    OpDef(5, 0, 10, "MSBI", "msbi", 0, []),
    OpDef(5, 0, 11, "IPOS", "ipos", 0, []),
    # unary float
    OpDef(5, 1, 1, "CITF", "citf", 0, []),
    OpDef(5, 1, 2, "NEGF", "negf", 0, []),
    OpDef(5, 1, 5, "ABSF", "absf", 0, []),
    OpDef(5, 1, 6, "INFZF", "infzf", 0, []),
    OpDef(5, 1, 7, "INFOEZF", "infoezf", 0, []),
    OpDef(5, 1, 8, "EQZF", "eqzf", 0, []),
    OpDef(5, 1, 9, "NEQZF", "neqzf", 0, []),
    OpDef(5, 1, 10, "SUPOEZF", "supoezf", 0, []),
    OpDef(5, 1, 11, "SUPZF", "supzf", 0, []),
    # binary int
    OpDef(6, 0, 0, "ADD", "add", 0, []),
    OpDef(6, 0, 1, "SUB", "sub", 0, []),
    OpDef(6, 0, 2, "MUL", "mul", 0, []),
    OpDef(6, 0, 3, "DIV", "div", 0, []),
    OpDef(6, 0, 4, "MOD", "mod", 0, []),
    OpDef(6, 0, 5, "AND", "and", 0, []),
    OpDef(6, 0, 6, "OR", "or", 0, []),
    OpDef(6, 0, 7, "XOR", "xor", 0, []),
    OpDef(6, 0, 8, "SLL", "sll", 0, []),
    OpDef(6, 0, 9, "SRA", "sra", 0, []),
    OpDef(6, 0, 10, "EQZV", "eqzv", 0, []),
    OpDef(6, 0, 11, "NEQZV", "neqzv", 0, []),
    # binary float
    OpDef(6, 1, 0, "ADDF", "addf", 0, []),
    OpDef(6, 1, 1, "SUBF", "subf", 0, []),
    OpDef(6, 1, 2, "MULF", "mulf", 0, []),
    OpDef(6, 1, 3, "DIVF", "divf", 0, []),
    OpDef(6, 1, 4, "MODF", "modf", 0, []),
    # branch
    OpDef(7, None, 0, "J", "jmp", Jump, [OpArg('imm16', Arg16 | NextRelative)]),
    OpDef(7, None, 1, "JNZ", "jnz", Conditional |
          Jump, [OpArg('imm16', Arg16 | NextRelative)]),
    OpDef(7, None, 2, "JZ", "jz",  Conditional |
          Jump, [OpArg('imm16', Arg16 | NextRelative)]),
    # gosub
    OpDef(8, None, None, "GOSUB", "gosub", Gosub, [
          OpArg('ssub', ArgSsub), OpArg('imm16', Arg16 | NextRelative)]),
    # other
    OpDef(9, None, 0, "EXIT", "halt", 0, []),
    OpDef(9, None, 1, "?", "exit", NeverReturn, []),
    OpDef(9, None, 2, "RET", "ret", GosubRet, []),
    OpDef(9, None, 3, "PUSH.CA", "drop", 0, []),
    OpDef(9, None, 5, "PUSH.C", "dup", 0, []),
    OpDef(9, None, 6, "SIN", "sin", 0, []),
    OpDef(9, None, 7, "COS", "cos", 0, []),
    OpDef(9, None, 8, "DEGR", "degr", 0, []),
    OpDef(9, None, 9, "RADD", "radd", 0, []),
    # syscall
    OpDef(10, None, None, "SYSCALL", "syscall",
          Syscall, [OpArg('ssub', ArgSsub), OpArg('imm16', Arg16)]),
    # 11 unk
    OpDef(11, None, None, "?", "gosub32", Gosub, [
          OpArg('ssub', ArgSsub), OpArg('imm32', Arg32 | NextRelative)]),
]
