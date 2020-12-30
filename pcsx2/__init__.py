# type hints for VSCode

from typing import Union, Callable


def ClearClient() -> None:
    pass


def WriteLn(text: str) -> None:
    pass


def AddBrk(addr: int, funct: Callable[[], None], brkf: int = 0) -> int:
    pass


def DelBrk(cookie: int) -> None:
    pass


def GetUL0(regName: Union[int, str]) -> int:
    pass


def SetUL0(regName: Union[int, str], value: int) -> None:
    pass


def SetPC(pc: int) -> None:
    pass


def ReadMem(start: int, length: int) -> bytes:
    pass


def ReadUI16(addr: int) -> int:
    pass


def ReadUI32(addr: int) -> int:
    pass


def ReadI16(addr: int) -> int:
    pass


def ReadUI16(addr: int) -> int:
    pass


def ReadByte(addr: int) -> int:
    pass


def WriteMem(buff: bytes, startIndex: int, addr: int, len: int) -> None:
    pass


def WriteByte(addr: int, value: int) -> None:
    pass


def WriteUI16(off: int, val: int) -> None:
    pass


def WriteUI32(off: int, val: int) -> None:
    pass


def AddRBrk(addr: int, length: int, funct: Callable[[int], None], brkf: int = 0) -> int:
    pass


def DelRBrk(cookie: int) -> None:
    pass


def AddWBrk(addr: int, length: int, funct: Callable[[int], None], brkf: int = 0) -> int:
    pass


def DelWBrk(cookie: int) -> None:
    pass


def pc() -> int:
    pass


def opc() -> int:
    pass


def isRec() -> bool:
    pass


def ElfCRC() -> int:
    pass


def Error(text: str) -> None:
    pass


def Warning(text: str) -> None:
    pass


def OnSuspend(funct: callable) -> None:
    pass


def OnResume(funct: callable) -> None:
    pass


def StartEETrace(filePathToBeginWrite: str) -> None:
    pass


def EndEETrace() -> None:
    pass


def SetRWTraceOptions(flags: int, funct: Callable[[bytes], None]) -> None:
    pass


def FlushRWTrace() -> None:
    pass


brkfReadOnly: int = 1
