from jinja2 import Environment, PackageLoader, select_autoescape
from ai import pcode
from ai import trap_table
from . import instr_docs
from typing import Union, Callable, List, Iterable, Tuple, Sequence, Dict
import datetime


class Syscall1:
    tableIdx: int
    funcIdx: int
    name: str
    doc: Dict
    funcForm: str


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
    syscallList: List = []

    def formFunc(name, opDef: pcode.OpDef) -> str:
        args = []
        for arg in opDef.args:
            args.append(arg.name)
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

    for opDef in pcode.table:
        behavior = opDef.behavior

        instr = Instr1()
        instr.part1 = opDef.opc
        instr.part2 = opDef.sub
        instr.part3 = opDef.ssub
        instr.name = opDef.name
        instr.funcForm = formFunc(instr.name, opDef)
        instr.doc = funcsDoc[instr.name] if instr.name in funcsDoc else {}
        instrList.append(instr)

    for tableIdx, table in enumerate(trap_table.tables):
        for funcIdx, func in enumerate(table):
            if len(func[0]) != 0:
                syscall = Syscall1()
                syscall.tableIdx = tableIdx
                syscall.funcIdx = funcIdx
                syscall.name = func[0]
                syscall.funcForm = syscall.name
                syscall.doc = funcsDoc[syscall.name] if syscall.name in funcsDoc else makeStubDocFrom(
                    syscall, func)
                syscallList.append(syscall)

    env = Environment(
        loader=PackageLoader("export_tools", 'templates'),
    )
    template = env.get_template('kh2ai.md.txt')
    return template.render(
        instrList=instrList,
        syscallList=syscallList,
        when=datetime.datetime.utcnow().strftime("%c UTC")
    )
