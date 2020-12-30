from xml.etree.ElementTree import Element, SubElement, tostring
from ai import pcode
from ai import trap_table

def run() -> str:
    root = Element('PCode')

    def partToStr(part):
        return str(part) if part != None else str(-1)

    def boolToXml(text):
        return "1" if text else "0"

    for array in pcode.table:
        flags = array[5]

        def setFlagsTo(instr):
            instr.set("ArgPart3", boolToXml(pcode.ArgPart3 & array[5]))
            instr.set("Arg16", boolToXml(pcode.Arg16 & array[5]))
            instr.set("Arg32", boolToXml(pcode.Arg32 & array[5]))
            instr.set("Syscall", boolToXml(pcode.Syscall & array[5]))
            instr.set("Gosub", boolToXml(pcode.Gosub & array[5]))
            instr.set("UnconditionalBranch", boolToXml(
                pcode.UnconditionalBranch & array[5]))
            instr.set("ConditionalBranch", boolToXml(
                pcode.ConditionalBranch & array[5]))
            instr.set("NeverReturn", boolToXml(pcode.NeverReturn & array[5]))
            instr.set("GosubRet", boolToXml(pcode.GosubRet & array[5]))

        if flags & pcode.Syscall:
            for tableIdx, table in enumerate(trap_table.tables):
                for funcIdx, func in enumerate(table):
                    if len(func[0]) != 0:
                        instr = SubElement(root, 'Instr')
                        instr.set("Part1", partToStr(array[0]))
                        instr.set("Part2", partToStr(tableIdx))
                        instr.set("Part3", partToStr(funcIdx))
                        instr.set("Name", func[0])
                        setFlagsTo(instr)
        else:
            instr = SubElement(root, 'Instr')
            instr.set("Part1", partToStr(array[0]))
            instr.set("Part2", partToStr(array[1]))
            instr.set("Part3", partToStr(array[2]))
            instr.set("Name", array[4])
            setFlagsTo(instr)

    return tostring(root, "unicode")
