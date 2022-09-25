from xml.etree.ElementTree import Element, SubElement, tostring
from ai import pcode
from ai import trap_table


def run() -> str:
    root = Element('PCode')

    def partToStr(part):
        return str(part) if part != None else str(-1)

    def boolToXml(text):
        return "1" if text else "0"

    for opDef in pcode.table:
        behavior = opDef.behavior

        instr = SubElement(root, 'Instr')
        instr.set("opcode", partToStr(opDef.opc))
        instr.set("sub", partToStr(opDef.sub))
        instr.set("ssub", partToStr(opDef.ssub))
        instr.set("name", opDef.name)

        instr.set("syscall", boolToXml(pcode.Syscall & behavior))
        instr.set("gosub", boolToXml(pcode.Gosub & behavior))
        instr.set("jump", boolToXml(pcode.Jump & behavior))
        instr.set("conditional", boolToXml(pcode.Conditional & behavior))
        instr.set("neverReturn", boolToXml(pcode.NeverReturn & behavior))
        instr.set("gosubRet", boolToXml(pcode.GosubRet & behavior))

        for opArg in opDef.args:
            arg = SubElement(instr, 'Arg')
            arg.set('name', opArg.name)
            if pcode.ArgSsub & opArg.flags:
                arg.set("type", "ssub")
            elif pcode.Arg16 & opArg.flags:
                arg.set("type", "imm16")
            elif pcode.Arg32 & opArg.flags:
                arg.set("type", "imm32")

            arg.set("aiPos", boolToXml(pcode.AiPos & opArg.flags))
            arg.set("nextRelative", boolToXml(pcode.NextRelative & opArg.flags))

    for tableIdx, table in enumerate(trap_table.tables):
        for funcIdx, func in enumerate(table["funcs"]):
            if len(func["name"]) != 0:
                syscall = SubElement(root, 'Syscall')
                syscall.set("tableIdx", partToStr(tableIdx))
                syscall.set("funcIdx", partToStr(funcIdx))
                syscall.set("name", func["name"])

    return tostring(root, "unicode")
