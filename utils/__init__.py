
import sys
import pcsx2
from typing import Union, Callable, Iterable, List
from itertools import groupby


class baseRedir:
    line = ""

    def write(self, data):
        self.line += data
        lf = self.line.find("\n")
        if lf != -1:
            self.writeln(self.line[0:lf])
            self.line = self.line[lf+1:]

    def flush(self):
        if len(self.line):
            self.writeln(self.line)
            self.line = ""
        pass

    def writeln(self, data):
        pass


class stdoutRedir(baseRedir):
    def writeln(self, data):
        pcsx2.WriteLn(data)


class stderrRedir(baseRedir):
    def writeln(self, data):
        pcsx2.Error(data)


def redirectStdoutStderr():
    sys.stderr = stderrRedir()
    sys.stdout = stdoutRedir()


class Brk:
    cookie = 0

    def __init__(self, addr: int, func: Callable[[], None], brkf: int = pcsx2.brkfReadOnly):
        self.cookie = pcsx2.AddBrk(addr, func, brkf)

    def __del__(self):
        if self.cookie != 0:
            pcsx2.DelBrk(self.cookie)


class RBrk:
    cookie = 0

    def __init__(self, addr: int, length: int, func: Callable[[int], None], brkf: int = pcsx2.brkfReadOnly):
        self.cookie = pcsx2.AddRBrk(addr, length, func, brkf)

    def __del__(self):
        if self.cookie != 0:
            pcsx2.DelRBrk(self.cookie)


class WBrk:
    cookie = 0

    def __init__(self, addr: int, length: int, func: Callable[[int], None], brkf: int = pcsx2.brkfReadOnly):
        self.cookie = pcsx2.AddWBrk(addr, length, func, brkf)

    def __del__(self):
        if self.cookie != 0:
            pcsx2.DelWBrk(self.cookie)


def GroupByPcAndCountAndOrderByDesc(pcList: Iterable[int]) -> Iterable:
    outList = []
    items = list(pcList)
    items.sort()
    for key, group in groupby(items, key=lambda it: it):
        outList.append((key, sum(1 for _ in group),))
    outList.sort(key=lambda it: -it[1])
    return outList


class GroupEntity:
    key = None
    values = None


def GroupBy(items, getKey):
    groups = []
    mapper = {}
    for item in items:
        key = getKey(item)
        if key in mapper:
            group = mapper[key]
        else:
            group = GroupEntity()
            group.key = key
            group.values = []
            groups.append(group)
            mapper[key] = group
        group.values.append(item)

    return groups


def bp(addr, brkf=pcsx2.brkfReadOnly):
    # Readonly break point
    def setbp(funct):
        pcsx2.AddBrk(addr, funct, brkf)
    return setbp


def rbp(addr, len, brkf=pcsx2.brkfReadOnly):
    # Readonly break point
    def setbp(funct):
        pcsx2.AddRBrk(addr, len, funct, brkf)
    return setbp


def wbp(addr, len, brkf=pcsx2.brkfReadOnly):
    # Readonly break point
    def setbp(funct):
        pcsx2.AddWBrk(addr, len, funct, brkf)
    return setbp
