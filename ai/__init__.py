import pcsx2
import recorders
import utils
from . import trap_table
import struct
from . import pcode


def traceAccessToSyscallTbl():
    @utils.rbrk(0x34dd00, 8*369)
    def got(target):
        pcsx2.WriteLn("# Read SyscallTbl pc %08X target %08X" %
                      (pcsx2.pc(), target,))


class ai_disasm:
    @staticmethod
    def decode(raw: bytes) -> str:
        # FEDCBA9876 54 3210
        # ----- opc typ pushOp
        # 0000000000 00 0000 u32: PUSH.V ri

        (code,) = struct.unpack("<H", raw[0:2])

        opc = (code & 15)
        sub = (code >> 4) & 3
        ssub = (code >> 6)

        for opDef in pcode.table:
            if opDef.opc == opc:
                if opDef.sub == None or opDef.sub == sub:
                    if opDef.ssub == None or opDef.ssub == ssub:
                        name = opDef.name

                        args = []
                        rawPos = 2
                        for opArg in opDef.args:
                            if pcode.ArgSsub & opArg.flags:
                                args.append(ssub)
                            elif pcode.Arg16 & opArg.flags:
                                # signed int16
                                args.append(struct.unpack(
                                    "<h", raw[rawPos:rawPos+2])[0])
                                rawPos += 2
                            elif pcode.Arg32 & opArg.flags:
                                # signed int32
                                args.append(struct.unpack(
                                    "<i", raw[rawPos:rawPos+4])[0])
                                rawPos += 4

                        if pcode.Syscall & opDef.behavior:
                            try:
                                funcIdx = args.pop()
                                name = trap_table.tables[ssub][funcIdx][0]
                            except IndexError:
                                # fallback
                                name = "syscall"
                                args.append(ssub)
                                args.append(args[0])

                        return name + " " + (", ".join(map(str, args)))

        return "Unk_%04X " % (code,)


class trace_ai_exec(recorders.base_recorder):
    filter = None
    oldTp = 0

    def toYN(self, value):
        return "Y" if value else "N"

    def toX2(self, value):
        return "%02X" % (value,)

    def loop(self):
        # s2: BD_PROCESS*
        # t6: pos2 (pc)
        process = pcsx2.GetUL0("s2")
        top = pcsx2.ReadUI32(process)
        if self.filter(top):
            pc = pcsx2.GetUL0("t6")
            readAddr = top + 16 + 2 * pc
            code = pcsx2.ReadUI16(readAddr)
            bytes6 = pcsx2.ReadMem(readAddr, 6)
            sp = pcsx2.ReadUI32(process + 8)
            tp = pcsx2.ReadUI32(process + 12)
            wp = pcsx2.ReadUI32(process + 16)

            # if self.oldTp != 0 and self.oldTp < tp:
            #    newTp = pcsx2.ReadMem(self.oldTp, tp - self.oldTp)
            #    pcsx2.WriteLn("  [%s]" % (" ".join(map(self.toX2, newTp))))
            #self.oldTp = tp

            # tpInfo = ",".join(map(lambda it: "%08X" % (it,), struct.unpack(
            #    "<10I", pcsx2.ReadMem(tp - 4*10, 4*10))))
            tpInfo = ""

            # base process pc sp tp wp code disasm
            pcsx2.WriteLn("b %07X p %07X pc %3X sp %07X tp %07X [%s] wp %s c %04X d %s" %
                          (top, process, pc, sp, tp, tpInfo, self.toYN(wp), code, ai_disasm.decode(bytes6)))


class trace_ai_exec_onload(trace_ai_exec):
    def end_file_load(self, file: str, addr: int, size: int):
        if file.endswith(".ard"):
            self.brk = utils.Brk(0x001da5a0, self.loop)
            self.filter = lambda target: (
                addr <= target and target < addr + size)


class trace_ai_exec_always(trace_ai_exec):
    def __init__(self):
        self.brk = utils.Brk(0x001da5a0, self.loop)
        self.filter = lambda target: True


def trap_all_funcs():
    # this won't work well.
    for table in trap_table.tables:
        for entry in table:
            if entry[1]:
                @utils.bp(entry[1])
                def disp():
                    pcsx2.WriteLn("@ " + entry[0])


def install_at_trap_call():
    addr2Name = {}

    def resolveFuncName(addr):
        return addr2Name.get(addr, "Unk_%08X" % (addr, ))

    @utils.bp(0x001dae80)
    def jalr():
        a0 = pcsx2.GetUL0("a0")
        t7 = pcsx2.GetUL0("t7")
        pcsx2.WriteLn("@ %s %08X" % (resolveFuncName(t7), a0, ))

    for table in trap_table.tables:
        for entry in table:
            if entry[1]:
                addr2Name[entry[1]] = entry[0]
