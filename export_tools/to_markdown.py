from jinja2 import Environment, PackageLoader, select_autoescape
from ai import pcode
from ai import trap_table
from . import instr_docs
from typing import Union, Callable, List, Iterable, Tuple, Sequence, Dict
import datetime


class Instr1:
    name: str
    part1: int
    part2: Union[int, None]
    part3: Union[int, None]
    doc: Dict
    funcForm: str


def run() -> str:
    funcsDoc = instr_docs.load()

    instrList: List[Instr1] = []

    def formFunc(name, array) -> str:
        args = []
        flags = array[5]
        if flags & pcode.ArgPart3:
            args.append("ssub_opc")
        if flags & pcode.Arg32:
            args.append("imm32")
        if flags & pcode.Arg16:
            args.append("imm16")
        return name + "  " + ",".join(args)

    def toMarkdownQuotes(text: str) -> str:
        res = ""
        for line in text.replace("\n", "\n\n").split('\n'):
            res += "> " + line + "\n"
        return res

    def makeStubDocFrom(instr, func) -> str:
        text = ""
        argc = func[2]
        count = argc & 65535
        hasReturn = argc & 0x40000000
        for idx in range(count):
            text += "arg%d = pop(); " % (count-idx,)
        funcArgs = ", ".join(map(lambda x: "arg%d" % (1+x), range(count)))
        text += "\n"
        if hasReturn:
            text += "return = %s(%s);\n" % (instr.name, funcArgs,)
            text += "push(return);\n"
        else:
            text += "%s(%s);\n" % (instr.name, funcArgs,)

        return {
            "help": toMarkdownQuotes(text.strip())
        }

    for array in pcode.table:
        flags = array[5]

        def setFlagsTo(instr):
            pass

        if flags & pcode.Syscall:
            for tableIdx, table in enumerate(trap_table.tables):
                for funcIdx, func in enumerate(table):
                    if len(func[0]) != 0:
                        instr = Instr1()
                        instr.part1 = array[0]
                        instr.part2 = tableIdx
                        instr.part3 = funcIdx
                        instr.name = func[0]
                        instr.funcForm = instr.name
                        instr.doc = funcsDoc[instr.name] if instr.name in funcsDoc else makeStubDocFrom(
                            instr, func)
                        instrList.append(instr)
                        setFlagsTo(instr)
        else:
            instr = Instr1()
            instr.part1 = array[0]
            instr.part2 = array[1]
            instr.part3 = array[2]
            instr.name = array[4]
            instr.funcForm = formFunc(instr.name, array)
            instr.doc = funcsDoc[instr.name] if instr.name in funcsDoc else {}
            instrList.append(instr)
            setFlagsTo(instr)

    env = Environment(
        loader=PackageLoader("export_tools", 'templates'),
    )
    template = env.get_template('kh2ai.md.txt')
    return template.render(instrList=instrList, when=datetime.datetime.utcnow().strftime("%c UTC"))
