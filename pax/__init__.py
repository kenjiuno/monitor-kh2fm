import pcsx2
import recorders
import utils
import struct
from . import ppp

pppTableStart = 0x00354c38


class trace_onload(recorders.base_recorder):
    pcList = []

    def end_file_load(self, file: str, addr: int, size: int):
        if file == "obj/WORLD_POINT.a.fm":
            self.brk = utils.RBrk(addr, size, self.read)

    def read(self, target):
        self.pcList.append(pcsx2.pc())

    def tick(self):
        if len(self.pcList) != 0:
            outList1 = utils.GroupByPcAndCountAndOrderByDesc(self.pcList)
            outList2 = map(lambda item: ("0x%08X" %
                                         (item[0],), item[1],), outList1)
            pcsx2.WriteLn("# read pax pc %s" % (str(tuple(outList2))))
            self.pcList.clear()


def install_access_to_pppProgTbl():
    base = 0x00354c38
    end = 0x00359000

    def read(target):
        # 241x18x4
        a = ((target - base) / 4) / 18
        b = ((target - base) / 4) % 18
        pcsx2.WriteLn("# read pppProgTbl pc %08X (%3d,%d)" %
                      (pcsx2.pc(), a, b))
    pcsx2.AddRBrk(base, end-base, read)


def install_call_ppp():
    def run1():
        idx = int((pcsx2.GetUL0("t6") - pppTableStart) / 4 / 18)
        a0 = pcsx2.GetUL0("a0")
        pcsx2.WriteLn("# pax1 %08X %s " % (a0, ppp.names[idx],))

    pcsx2.AddBrk(0x001e7a58, run1)

    def run2():
        idx = int((pcsx2.GetUL0("t5") - pppTableStart) / 4 / 18)
        a0 = pcsx2.GetUL0("a0")
        pcsx2.WriteLn("# pax2 %08X %s " % (a0, ppp.names[idx],))

    pcsx2.AddBrk(0x001e78b4, run2)

    def run3():
        idx = int((pcsx2.GetUL0("t6") - pppTableStart) / 4 / 18)
        a0 = pcsx2.GetUL0("a0")
        pcsx2.WriteLn("# pax3 %08X %s " % (a0, ppp.names[idx],))

    pcsx2.AddBrk(0x001e79b0, run3)
