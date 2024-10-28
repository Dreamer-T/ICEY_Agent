import win32gui
import win32api
import win32process
import ctypes as c
from ctypes import wintypes as w


Psapi = c.WinDLL('Psapi.dll')


PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010


def EnumProcessModulesEx(hProcess):
    buf_count = 256
    while True:
        LIST_MODULES_ALL = 0x03
        buf = (w.HMODULE * buf_count)()
        buf_size = c.sizeof(buf)
        needed = w.DWORD()
        if not Psapi.EnumProcessModulesEx(hProcess, c.byref(buf), buf_size, c.byref(needed), LIST_MODULES_ALL):
            raise OSError('EnumProcessModulesEx failed')
        if buf_size < needed.value:
            buf_count = needed.value // (buf_size // buf_count)
            continue
        count = needed.value // (buf_size // buf_count)
        return map(w.HMODULE, buf[:count])


class State():
    def __init__(self, gameName, baseOffsetOfMono, bossOffset, playerOffset) -> None:
        """
        gameName 表示游戏窗口所显示的名字用以获得游戏进程号

        baseOffsetOfMono 表示游戏基址基于mono.dll的偏移量

        bossOffset 表示游戏内BOSS的血量偏移地址列表

        playerOffset 表示游戏内玩家的血量偏移地址列表
        """
        self.bossOffset = bossOffset
        self.playerOffset = playerOffset
        hd = win32gui.FindWindow(None, gameName)
        pid = win32process.GetWindowThreadProcessId(hd)[1]
        self.pid = pid
        k32 = c.windll.LoadLibrary("C:\\Windows\\System32\\kernel32.dll")
        self.process_handle = win32api.OpenProcess(0x1F0FFF, False, pid)

        # get dll address
        hProcess = k32.OpenProcess(
            PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
            False, pid)
        hModule = EnumProcessModulesEx(hProcess)
        for i in hModule:
            temp = win32process.GetModuleFileNameEx(
                self.process_handle, i.value)
            if temp[-8:] == "mono.dll":
                self.mono = i.value + baseOffsetOfMono
        OpenProcess = k32.OpenProcess
        OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
        OpenProcess.restype = w.HANDLE

        self.ReadProcessMemory = k32.ReadProcessMemory
        self.ReadProcessMemory.argtypes = [w.HANDLE, w.LPCVOID,
                                           w.LPVOID, c.c_size_t, c.POINTER(c.c_size_t)]
        self.ReadProcessMemory.restype = w.BOOL

        GetLastError = k32.GetLastError
        GetLastError.argtypes = None
        GetLastError.restype = w.DWORD

        self.CloseHandle = k32.CloseHandle
        self.CloseHandle.argtypes = [w.HANDLE]
        self.CloseHandle.restype = w.BOOL

        self.processHandle = OpenProcess(0x10, False, pid)

    def getPlayerHp(self) -> int:
        """
        获取玩家血量
        """
        data = c.c_ulonglong()
        bytesRead = c.c_ulonglong()
        self.ReadProcessMemory(self.processHandle, self.mono, c.byref(
            data), c.sizeof(data), c.byref(bytesRead))
        for num in self.playerOffset:
            self.ReadProcessMemory(self.processHandle, data.value + num, c.byref(
                data), c.sizeof(data), c.byref(bytesRead))
        a = '{:016X}'.format(data.value)
        hpx = a[-2:]
        # self.CloseHandle(self.processHandle)
        return int(hpx, 16)

    def getBossHp(self) -> int:
        """
        获取游戏内BOSS血量
        """
        data = c.c_ulonglong()
        bytesRead = c.c_ulonglong()
        self.ReadProcessMemory(self.processHandle, self.mono, c.byref(
            data), c.sizeof(data), c.byref(bytesRead))
        for num in self.bossOffset:
            self.ReadProcessMemory(self.processHandle, data.value + num, c.byref(
                data), c.sizeof(data), c.byref(bytesRead))
        a = '{:016X}'.format(data.value)
        hpx = a
        # self.CloseHandle(self.processHandle)
        return int(hpx, 16)


# playerOffset = [0x190, 0x58, 0x4A0, 0x60, 0x208, 0x78, 0x20]
# bossOffset = [0x190, 0x58, 0x3D8, 0x0, 0xA8, 0x0, 0x94]

# state = State("ICEY", 0x0264690, bossOffset, playerOffset)

# while 1:
#     print(state.getBossHp())
