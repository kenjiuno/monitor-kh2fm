from jinja2 import Environment, PackageLoader, select_autoescape
from ai import pcode
from ai import trap_table
import utils
from typing import Union, Callable, List, Iterable, Tuple, Sequence, Dict
from . import instr_docs


class SingleInstrument:
    name: str
    args: List[str]
    conditions: List[str]
    doc: Dict


class MixedInstrument:
    name: str
    args: str
    conditions: str
    doc: Dict

    def __init__(self, instrList: Sequence[SingleInstrument]):
        self.name = instrList[0].name
        self.args = ",".join(instrList[0].args)
        argsAppend = ""
        for arg in instrList[0].args:
            argsAppend += "; " + arg
        self.conditions = " | ".join(
            map(
                lambda instr: "(" + (" & ".join(instr.conditions)) + ")",
                instrList
            )
        ) + argsAppend
        self.doc = instrList[0].doc


def run() -> str:
    instrList: List[SingleInstrument] = []

    def partToStr(part):
        return str(part) if part != None else str(-1)

    def boolToXml(text):
        return "1" if text else "0"

    funcsDoc = instr_docs.load()

    def buildInstr(instr: SingleInstrument, part1, part2, part3, arg16Value, flags):
        Arg32 = bool(pcode.Arg32 & flags)
        Arg16 = bool(pcode.Arg16 & flags)
        ArgPart3 = bool(pcode.ArgPart3 & flags)
        Gosub = bool(pcode.Gosub & array[5])
        Syscall = bool(pcode.Syscall & array[5])
        UnconditionalBranch = bool(pcode.UnconditionalBranch & array[5])
        ConditionalBranch = bool(pcode.ConditionalBranch & array[5])
        Branch = bool(Gosub or UnconditionalBranch or ConditionalBranch)

        if True:
            args = []
            cond = []

            if Arg32:
                args.append("full_ext")
            elif Branch:
                args.append("LABEL8")
            elif ArgPart3 and Arg16:
                args.append("rn")
                args.append("ope2")
            elif Arg16:
                args.append("ope2")

            # :push.v full_ext is opcode=0 & ( sub_opc=1 | sub_opc=0 ) ; full_ext {
            # :push2_unk0 is opcode_ext=0 & sub_opc_ext=2 & opesub=0  {
            # :push.ap rn, ope2 is opcode_ext=0 & sub_opc_ext=2 & opesub=1 & ope2 & rn {
            # :cfti is opcode=5 & sub_opc=0 & ssub_opc=0
            # :jmp ope3, LABEL8 is opcode_ext=8 & LABEL8 & ope3

            if Syscall:
                cond.append("opcode_ext=%d" % (part1,))
                if part2 != None:
                    raise RuntimeError()
                if part3 != None:
                    cond.append("ope3=%d" % (part3,))
                if arg16Value != None:
                    cond.append("ope2=%d" % (arg16Value,))
            elif Arg16:
                cond.append("opcode_ext=%d" % (part1,))
                if part2 != None:
                    cond.append("sub_opc_ext=%d" % (part2,))
                if part3 != None:
                    cond.append("ope3=%d" % (part3,))
                if arg16Value != None:
                    cond.append("ope2=%d" % (arg16Value,))
            else:
                cond.append("opcode=%d" % (part1,))
                if part2 != None:
                    cond.append("sub_opc=%d" % (part2,))
                if part3 != None:
                    cond.append("ssub_opc=%d" % (part3,))
                if arg16Value != None:
                    raise RuntimeError()

            instr.args = args
            instr.conditions = cond
            instr.doc = funcsDoc[instr.name] if instr.name in funcsDoc else {}

            # Note about "7.4.4.1. The ';' Operator", see
            # https://ghidra.re/courses/languages/html/sleigh_constructors.html

    for array in pcode.table:
        flags = array[5]

        if flags & pcode.Syscall:
            for tableIdx, table in enumerate(trap_table.tables):
                for funcIdx, func in enumerate(table):
                    if len(func[0]) != 0:
                        instr = SingleInstrument()
                        instr.name = func[0]
                        buildInstr(instr, array[0],
                                   None, tableIdx, funcIdx, pcode.Syscall)
                        instrList.append(instr)
        else:
            instr = SingleInstrument()
            instr.name = array[4]
            buildInstr(instr, array[0], array[1], array[2], None, array[5])
            instrList.append(instr)

    mixedInstrList = []
    if True:
        registeredNames = {}
        for instr in instrList:
            mixedInstr = MixedInstrument((instr,))
            name = mixedInstr.name
            for x in range(100):
                altName = name
                if x != 0:
                    altName += "_%d" % (1+x,)
                if altName in registeredNames:
                    continue
                name = altName
                break

            registeredNames[name] = None

            mixedInstr.name = name
            mixedInstrList.append(mixedInstr)

    env = Environment(
        loader=PackageLoader("export_tools", 'templates'),
    )
    template = env.get_template('kh2ai.sinc.txt')
    return template.render(instrList=mixedInstrList)
