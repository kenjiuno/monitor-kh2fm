#!pcsx2py

# This volatile module `monitor.F266B00B` may be re-loaded and loose all variables on some events:
# - Game startup (on _reloadElfInfo)
# - Resume, where it is suspended by pressing ESC key (on AppCoreThread::Resume)
# Not:
# - Resume, where it is suspended by System menu → Pause
# - Load game state

import pcsx2
import os
from pathlib import Path
import sys
from . import utils
from . import main
from . import recorders
from . import ai
from . import pax


utils.redirectStdoutStderr()

# config
extractFiles = False
recordReadMemFrm = False
traceAiExec = False
tracePax = False
showTick = False

# internal variables please do not change
filePath = None
addrToLoad = 0
injectSize = 0
injectPostProcess = False

fileFindPath = False

exeDir = Path(__file__).parent.parent

bp = utils.bp

recorder = recorders.null_recorder()
# recorder = recorders.one_time_recorder(exeDir.joinpath('oneround.bin'))
# recorder = recorders.ee_load_store_recorder(
#     'H:/Proj/khkh_xldM/MEMO/expSim/ardTrace/readmemfrm.txt')
# recorder = recorders.ee_load_store_recorder_try2(
#     'H:/Proj/khkh_xldM/MEMO/expSim/ardTrace/readmemfrm.txt')
# recorder = recorders.ee_load_store_recorder_try3(
#     'H:/Proj/khkh_xldM/MEMO/expSim/ardTrace/readmemfrm.txt')
# recorder = recorders.ee_load_store_recorder_try4(
#     Path('H:/Proj/khkh_xldM/MEMO/expSim/ardTrace'))
recorder = recorders.recorder_repeater()

if recordReadMemFrm:
    recorder.register(
        recorders.ee_load_store_recorder_try4(
            Path('H:/Proj/khkh_xldM/MEMO/expSim/ardTrace'),
            endsWith=".ard"
        )
    )

# ai.traceAccessToSyscallTbl()

if traceAiExec:
    # recorder.register(ai.trace_ai_exec_onload())
    # recorder.register(ai.trace_ai_exec_always())
    # ai.trap_all_funcs()
    # ai.install_at_trap_call()
    pass

if tracePax:
    # recorder.register(pax.trace_onload())
    # pax.install_access_to_pppProgTbl()
    # pax.install_call_ppp()
    recorder.register(
        recorders.ee_load_store_recorder_try4(
            Path('H:/Proj/khkh_xldM/MEMO/expSim/paxTrace'),
            endsWith="obj/WORLD_POINT.a.fm"
        )
    )
    pass


if False:
    # this is F_memcpy
    @bp(0x002fdd68)
    def FUN_002fdd68():
        pcsx2.WriteLn("# FUN_002fdd68 %08X %08X %08X" %
                      (pcsx2.GetUL0("a0"), pcsx2.GetUL0("a1"), pcsx2.GetUL0("a2"),))

    @bp(0x002fdd8c)
    def x1():
        pcsx2.WriteLn("#           lq %08X" %
                      (pcsx2.GetUL0("a1"),))

    @bp(0x002fdd9c)
    def x1():
        pcsx2.WriteLn("#           sq %08X" %
                      (pcsx2.GetUL0("a3"),))

    @bp(0x002fdda4)
    def x2():
        pcsx2.WriteLn("#           lq %08X" %
                      (pcsx2.GetUL0("a1"),))

    @bp(0x002fddac)
    def x2():
        pcsx2.WriteLn("#           sq %08X" %
                      (pcsx2.GetUL0("a3"),))

    @bp(0x002fddd4)
    def x2():
        pcsx2.WriteLn("#           sd %08X" %
                      (pcsx2.GetUL0("a3"),))

    @bp(0x002fde00)
    def x2():
        pcsx2.WriteLn("#           sb %08X" %
                      (pcsx2.GetUL0("v1"),))

    @bp(0x002fde10)
    def FUN_002fdd68_jr():
        pcsx2.WriteLn("#              %08X " % (pcsx2.GetUL0("t0"),))


@bp(0x0016d2a0)
def trap_puti():
    a0 = pcsx2.GetUL0("a0")
    val = pcsx2.ReadI32(a0)
    pcsx2.WriteLn("# trap_puti %d" % (val,))


@bp(0x0016d2a8)
def trap_putf():
    a0 = pcsx2.GetUL0("a0")
    pcsx2.WriteLn("# trap_putf %08X" % (a0,))


@bp(0x0016d2b0)
def trap_puts():
    a0 = pcsx2.GetUL0("a0")
    a0v = pcsx2.ReadUI32(a0)
    val = pcsx2.ReadMem(a0v, 32).decode("latin1").split("\x00")[0]
    pcsx2.WriteLn("# trap_puts %08X %08X '%s'" % (a0, a0v, val))


@bp(0x001adf00)
def S_IEXPA():
    # desc: load file from DVD into memory
    # in a0: filePath
    # in a1: addrToLoad
    # out v0 : fileSizeLoadedActually
    a0 = pcsx2.GetUL0('a0')
    global filePath
    filePath = pcsx2.ReadMem(a0, 32).decode('latin1').split('\0')[0]
    global addrToLoad
    addrToLoad = pcsx2.GetUL0('a1')
    recorder.begin_file_load(filePath, addrToLoad)
    pcsx2.WriteLn("# py.S_IEXPA: %08x  %s " % (addrToLoad, filePath, ))

    global injectPostProcess
    injectPostProcess = False

    try:
        injectFrom = exeDir.joinpath(
            "inject.%08x\\%s" % (pcsx2.ElfCRC(), filePath, ))
        with open(str(injectFrom), 'rb') as file:
            injectData = file.read()
            global injectSize
            injectSize = len(injectData)

            pcsx2.WriteMem(injectData, 0, addrToLoad, injectSize)

            injectPostProcess = True

            pcsx2.WriteLn('#    S_IEXPA: Inject ok. %u ' % (injectSize, ))

    except FileNotFoundError:
        pass


@bp(0x001adf04, 0)
def S_IEXPA_AT4():
    if injectPostProcess:
        pcsx2.SetUL0('v0', injectSize)
        pcsx2.SetPC(0x001ae004)  # jump to this program address

        recorder.end_file_load(filePath, addrToLoad, pcsx2.GetUL0('v0'))


@bp(0x001ae004)
def E_IEXPA():
    if extractFiles and (filePath != '') and (addrToLoad != 0) and (not injectPostProcess):
        extractTo = exeDir.joinpath('expa.%08x\\%s' %
                                    (pcsx2.ElfCRC(), filePath, ))
        os.makedirs(str(extractTo.parent), 0o777, True)
        with open(str(extractTo), 'wb') as file:
            extractSize = pcsx2.GetUL0('v0')
            extractData = pcsx2.ReadMem(addrToLoad, extractSize)
            file.write(extractData)

            pcsx2.WriteLn('#    E_IEXPA: Out ok. ')

    recorder.end_file_load(filePath, addrToLoad, pcsx2.GetUL0('v0'))


@bp(0x001ae308)
def S_FINDX():
    # desc: get file info
    # in a1: filePath
    # out v0: idx entry pointer
    a1 = pcsx2.GetUL0('a1')
    global fileFindPath
    fileFindPath = pcsx2.ReadMem(a1, 32).decode('latin1').split('\0')[0]


@bp(0x001ae454)
def E_FINDX():
    try:
        injectFrom = exeDir.joinpath(
            "inject.%08x\\%s" % (pcsx2.ElfCRC(), fileFindPath, ))

        injectSize = os.stat(str(injectFrom)).st_size

        idxPointer = pcsx2.GetUL0('v0')
        if idxPointer:
            sizeInEntry = pcsx2.ReadUI32(idxPointer + 12)

            if sizeInEntry != injectSize:
                pcsx2.WriteUI32(idxPointer + 12, injectSize)

                pcsx2.WriteLn(
                    '# py.E_FINDX: Entry %s resized to %u (from %u) ' % (fileFindPath, injectSize, sizeInEntry, ))

    except FileNotFoundError:
        pass


@bp(0x00101e94)
def TickIncr():
    if showTick:
        pcsx2.WriteLn('# Tick %d' % (pcsx2.GetUL0('t7'),))
    recorder.tick()


@pcsx2.OnSuspend
def onSuspend():
    recorder.suspend()
    pass


@pcsx2.OnResume
def onResume():
    pass
