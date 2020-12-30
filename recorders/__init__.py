import pcsx2
import io
import utils
from struct import *
from pathlib import Path
import time
from typing import List, Type

# This is non-volatile module. pcsx2 restart is required to reload this module.


class base_recorder:
    def tick(self):
        pass

    def suspend(self):
        pass

    def begin_file_load(self, file: str, addr: int):
        pass

    def end_file_load(self, file: str, addr: int, size: int):
        pass


class null_recorder(base_recorder):
    pass


class one_time_recorder(base_recorder):
    def __init__(self, saveTo):
        self.saveTo = saveTo
        self.state = 0

    def tick(self):
        if pcsx2.isRec():
            return

        if self.state == 0:
            self.state = 1
            pcsx2.WriteLn("# StartEETrace")
            pcsx2.StartEETrace(str(self.saveTo))
        elif self.state == 1:
            self.state = 2
            pcsx2.WriteLn("# EndEETrace")
            pcsx2.EndEETrace()

    def suspend(self):
        if self.state == 1:
            self.state = 2
            pcsx2.WriteLn("# EndEETrace")
            pcsx2.EndEETrace()


class ee_load_store_recorder(base_recorder):
    def __init__(self, saveTo):
        self.saveTo = saveTo
        self.state = 0
        self.cnt = 0
        self.logLines = []

    def begin_file_load(self, file: str, addr: int):
        if file.endswith(".ard"):
            self.state = 1
            self.cnt = 0
            pcsx2.SetRWTraceOptions(0, None)
            pcsx2.FlushRWTrace()
            pcsx2.SetRWTraceOptions(1, self.flush_rw_buffer)

    def flush_rw_buffer(self, buff: bytes):
        for (pc, target, flags) in iter_unpack("<III", buff):
            self.cnt += 1
            self.logLines.append("%08X %08X" % (pc, target))

    def tick(self):
        if self.state == 1:
            self.state = 2
            pcsx2.FlushRWTrace()
            pcsx2.SetRWTraceOptions(0, None)
            pcsx2.WriteLn("# %d records..." % (self.cnt,))

            with open(self.saveTo, "w") as f:
                f.write("\n".join(self.logLines))


class ee_load_store_recorder_try2(base_recorder):
    def __init__(self, saveTo):
        self.saveTo = saveTo
        self.state = 0
        self.numRead = 0
        self.numReadHit = 0
        self.logLines = []
        self.addrFrom = 0
        self.addrTo = 0

    def end_file_load(self, file: str, addr: int, size: int):
        # 01c4d440  ard/eh18.ard
        if file.endswith(".ard"):
            self.state = 1
            self.numRead = 0
            self.numReadHit = 0
            self.logLines = []
            self.addrFrom = addr
            self.addrTo = addr + size
            pcsx2.SetRWTraceOptions(0, None)
            pcsx2.FlushRWTrace()
            pcsx2.SetRWTraceOptions(1, self.flush_rw_buffer)

    def flush_rw_buffer(self, buff: bytes):
        for (pc, target, flags) in iter_unpack("<III", buff):
            self.numRead += 1
            if self.addrFrom <= target and target < self.addrTo:
                self.numReadHit += 1
                self.logLines.append("%08X %08X" % (pc, target))

    def tick(self):
        if self.state == 1:
            pcsx2.FlushRWTrace()
            pcsx2.WriteLn("# read:%d hit:%d total:%d" %
                          (self.numRead, self.numReadHit, len(self.logLines)))
            self.numRead = 0
            self.numReadHit = 0

    def suspend(self):
        self.state = 2

        pcsx2.FlushRWTrace()
        pcsx2.SetRWTraceOptions(0, None)

        pcsx2.WriteLn("# writing down it.")
        with open(self.saveTo, "w") as f:
            f.write("\n".join(self.logLines))


class ee_load_store_recorder_try3(base_recorder):
    state = 0
    numRead = 0
    numReadHit = 0
    logLines = []

    def __init__(self, saveTo):
        self.saveTo = saveTo

    def end_file_load(self, file: str, addr: int, size: int):
        # 01c4d440  ard/eh18.ard
        if file.endswith(".ard"):
            self.state = 1
            self.numRead = 0
            self.numReadHit = 0
            self.logLines = []
            self.brk = utils.RBrk(addr, size, self.read_hit)

    def read_hit(self, target: int):
        self.numRead += 1
        self.numReadHit += 1
        self.logLines.append("%08X %08X" % (pcsx2.pc(), target))

    def tick(self):
        if self.state == 1:
            # pcsx2.FlushRWTrace()
            # pcsx2.WriteLn("# read:%d hit:%d total:%d" %
            #               (self.numRead, self.numReadHit, len(self.logLines)))
            # self.numRead = 0
            # self.numReadHit = 0
            pass

    def suspend(self):
        if self.state == 1:
            self.state = 2

            pcsx2.WriteLn("# Written %d hits." % (len(self.logLines),))
            with open(self.saveTo, "w") as f:
                f.write("\n".join(self.logLines))


class ee_load_store_recorder_try4(base_recorder):
    state = 0
    logLines = []
    saveDir: Path = None
    saveDirNow: Path = None
    pcsx2Log = []

    def __init__(self, saveDir: Path):
        self.saveDir = saveDir

    def end_file_load(self, file: str, addr: int, size: int):
        # 01c4d440  ard/eh18.ard
        if file.endswith(".ard"):
            self.state = 1
            self.write_down()
            self.pcsx2Log.append("# py.S_IEXPA: %08X  %s " % (addr, file))
            self.brk = utils.RBrk(addr, size, self.read_hit)
            self.saveDirNow = self.saveDir.joinpath(
                "%s_%d" % (Path(file).name, int(time.time()),))
            self.saveDirNow.mkdir(parents=True, exist_ok=True)

    def read_hit(self, target: int):
        self.logLines.append("%08X %08X" % (pcsx2.pc(), target))

    def tick(self):
        pass

    def suspend(self):
        if self.state == 1:
            self.state = 2

            self.write_down()

    def write_down(self):
        if self.saveDirNow != None:
            pcsx2.WriteLn("# Written %d hits." % (len(self.logLines),))

            with open(str(self.saveDirNow.joinpath('readmemfrm.txt')), "w") as f:
                f.write("\n".join(self.logLines))
                self.logLines = []
            with open(str(self.saveDirNow.joinpath('pcsx2.log')), "w") as f:
                f.write("\n".join(self.pcsx2Log))
                self.pcsx2Log = []


class recorder_repeater(base_recorder):
    list: List[base_recorder] = []

    def register(self, ob: Type[base_recorder]):
        self.list.append(ob)

    def unregister(self, ob: Type[base_recorder]):
        self.list.remove(ob)

    def tick(self, *args, **kwargs):
        for ob in self.list:
            ob.tick(*args, **kwargs)

    def suspend(self, *args, **kwargs):
        for ob in self.list:
            ob.suspend(*args, **kwargs)

    def begin_file_load(self, *args, **kwargs):
        for ob in self.list:
            ob.begin_file_load(*args, **kwargs)

    def end_file_load(self, *args, **kwargs):
        for ob in self.list:
            ob.end_file_load(*args, **kwargs)
