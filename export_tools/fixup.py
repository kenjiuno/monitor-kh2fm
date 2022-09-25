from ai import trap_table_legacy
from ai import trap_table
import json


def ver2() -> str:
    newTables = []

    for tableIdx, table in enumerate(trap_table_legacy.tables):
        newFuncs = []
        newTable = {
            "tableIndex": tableIdx,
            "funcs": newFuncs,
        }
        for funcIdx, func in enumerate(table):
            argc = func[2] & 65535
            hasRet = func[2] & 0x40000000
            newFunc = {
                "index": funcIdx,
                "name": func[0],
                "addr": func[1],
                "flags": func[2],
                "args": list(map(lambda idx: {"type": "unknown", "name": "unk%d" % (1+idx,)}, range(argc))),
                "ret": [{"type": "unknown", "name": "unk"}] if hasRet else [{"type": "void", "name": "x"}]
            }
            newFuncs.append(newFunc)

        newTables.append(newTable)
    return json.dumps(newTables, indent=1)

def ver3() -> str:
    for table in trap_table.tables:
        for func in table["funcs"]:
            for arg in func["args"]:
                arg["desc"] = ""
            for arg in func["ret"]:
                arg["desc"] = ""

    return json.dumps(trap_table.tables, indent=1)
