from jinja2 import Environment, PackageLoader, select_autoescape
from ai import pcode


def norm(one: any) -> str:
    if one == None:
        return "x"
    else:
        return str(one)


def makeItalic(token: str) -> str:
    return "_" + token + "_"


class wrapOpDef:
    code: str
    name: str
    description: str

    def __init__(self, op: pcode.OpDef):
        self.code = "%s,%s,%s" % (norm(op.opc), norm(op.sub), norm(op.ssub))
        self.name = op.name
        self.oldName = ", ".join(map(makeItalic, op.oldnames))
        self.description = op.desc


def run() -> str:
    opcodeList = map(lambda it: wrapOpDef(it), pcode.table)

    env = Environment(
        loader=PackageLoader("export_tools", "templates"),
    )
    template = env.get_template("md_opc.txt")
    return template.render(opcodeList=opcodeList)
