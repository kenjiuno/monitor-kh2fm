from ai import pcode
from ai import trap_table


def enums() -> str:
    body = ""

    for opDef in pcode.table:
        body += "%s = 0x%04X,\n" % (opDef.name, (opDef.opc) |
                                    ((opDef.sub or 0) << 4) | ((opDef.ssub or 0) << 6))

    return body


def traps() -> str:
    lines = []
    for tableIdx, table in enumerate(trap_table.tables):
        for trapIdx, trap in enumerate(table["funcs"]):
            if trap["name"]:
                assigns = []
                assigns.append("TableIndex = %d" % (tableIdx,))
                assigns.append("TrapIndex = %d" % (trapIdx,))
                assigns.append("Name = \"%s\"" % (trap["name"],))
                assigns.append("Flags = 0x%08X" % (trap["flags"],))

                lines.append("\t\t\tnew BdxTrap { %s }," % (
                    ", ".join(assigns),))
    return "\n".join(lines)


def descs() -> str:
    body = ""
    lines = []

    for opDef in pcode.table:
        word = (opDef.opc) | ((opDef.sub or 0) << 4) | ((opDef.ssub or 0) << 6)
        mask = (
            0x000F
            | (0 if opDef.sub == None else 0x0030)
            | (0 if opDef.ssub == None else 0xFFC0)
        )

        assigns = []
        assigns.append("Code = 0x%04X" % (word,))
        assigns.append("CodeMask = 0x%04X" % (mask,))
        assigns.append("Name = \"%s\"" % (opDef.name,))

        if True:
            behavior = opDef.behavior
            if pcode.Syscall & behavior:
                assigns.append("IsSyscall = true")
            if pcode.Gosub & behavior:
                assigns.append("IsGosub = true")
            if pcode.Jump & behavior:
                assigns.append("IsJump = true")
            if pcode.Conditional & behavior:
                assigns.append("IsJumpConditional = true")
            if pcode.NeverReturn & behavior:
                assigns.append("NeverReturn = true")
            if pcode.GosubRet & behavior:
                assigns.append("IsGosubRet = true")

            newArgs = []

            codeSize = 1

            for opArg in opDef.args:
                subAssigns = []
                subAssigns.append("Name = \"%s\"" % (opArg.name,))
                if pcode.ArgSsub & opArg.flags:
                    subAssigns.append("Type = ArgType.Ssub")
                elif pcode.Arg16 & opArg.flags:
                    subAssigns.append("Type = ArgType.Imm16")
                    codeSize += 1
                elif pcode.Arg32 & opArg.flags:
                    subAssigns.append("Type = ArgType.Imm32")
                    codeSize += 2

                if pcode.AiPos & opArg.flags:
                    subAssigns.append("AiPos = true")
                if pcode.NextRelative & opArg.flags:
                    subAssigns.append("IsRelative = true")

                newArgs.append("new Arg { %s }" % (", ".join(subAssigns)))

            assigns.append("CodeSize = %d" % (codeSize,))

            if 1 <= len(newArgs):
                assigns.append("Args = new[] { %s }" % (", ".join(newArgs),))

        lines.append("\t\t\tnew BdxInstructionDesc { %s }," % (
            ", ".join(assigns),))

    return "\n".join(lines)
