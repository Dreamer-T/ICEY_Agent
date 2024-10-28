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
    def __init__(self, gameName, baseOffsetOfMono, bossHpOffset, playerHpOffset, playerYOffset) -> None:
        """
        gameName 表示游戏窗口所显示的名字用以获得游戏进程号

        baseOffsetOfMono 表示游戏基址基于 mono.dll 的偏移量

        # baseOffsetOfGame 表示游戏基址基于 游戏程序.exe 的偏移量

        bossOffset 表示游戏内BOSS的血量偏移地址列表

        playerOffset 表示游戏内玩家的血量偏移地址列表
        """
        self.bossHpOffset = bossHpOffset
        self.playerHpOffset = playerHpOffset
        self.playerYOffset = playerYOffset
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
            # if temp[-8:] == "ICEY.exe":
            #     self.game = i.value+baseOffsetOfGame
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

    def getPlayerPositionX(self) -> int:
        data = c.c_ulonglong()
        bytesRead = c.c_ulonglong()
        self.ReadProcessMemory(self.processHandle, 0x7FFE6B470000+0x261A28, c.byref(
            data), c.sizeof(data), c.byref(bytesRead))
        offsets = [0xE0, 0x8D0, 0xAD0, 0x0, 0x38]
        for num in offsets:
            self.ReadProcessMemory(self.processHandle, data.value + num, c.byref(
                data), c.sizeof(data), c.byref(bytesRead))
        x = c.c_float()
        self.ReadProcessMemory(
            self.processHandle, data.value + 0x8, c.byref(x), c.sizeof(data), c.byref(bytesRead))
        # self.ReadProcessMemory(self.processHandle, self.mono, c.byref(
        #     data), c.sizeof(data), c.byref(bytesRead))
        # offsets = [0xF8, 0x8, 0x10, 0x98, 0x940]
        # for num in offsets:
        #     self.ReadProcessMemory(self.processHandle, data.value + num, c.byref(
        #         data), c.sizeof(data), c.byref(bytesRead))
        # y = c.c_float()
        # self.ReadProcessMemory(
        #     self.processHandle, data.value+0xA30, c.byref(y), c.sizeof(data), c.byref(bytesRead))

        # return x.value, y.value
        return x.value

    def getPlayerPositionY(self) -> int:
        data = c.c_ulonglong()
        bytesRead = c.c_ulonglong()
        self.ReadProcessMemory(self.processHandle, self.mono, c.byref(
            data), c.sizeof(data), c.byref(bytesRead))
        offsets = [0x190, 0x58, 0x148, 0x10, 0x380]
        for num in offsets:
            self.ReadProcessMemory(self.processHandle, data.value + num, c.byref(
                data), c.sizeof(data), c.byref(bytesRead))
        y = c.c_float()
        self.ReadProcessMemory(
            self.processHandle, data.value + 0xC0, c.byref(y), c.sizeof(data), c.byref(bytesRead))
        # self.ReadProcessMemory(self.processHandle, self.mono, c.byref(
        #     data), c.sizeof(data), c.byref(bytesRead))
        # offsets = [0xF8, 0x8, 0x10, 0x98, 0x940]
        # for num in offsets:
        #     self.ReadProcessMemory(self.processHandle, data.value + num, c.byref(
        #         data), c.sizeof(data), c.byref(bytesRead))
        # y = c.c_float()
        # self.ReadProcessMemory(
        #     self.processHandle, data.value+0xA30, c.byref(y), c.sizeof(data), c.byref(bytesRead))

        # return x.value, y.value
        return y.value


# playerOffset = [0x190, 0x58, 0x4A0, 0x60, 0x208, 0x78, 0x20]
# bossOffset = [0x190, 0x58, 0x3D8, 0x0, 0xA8, 0x0, 0x94]
# # 0x261A28 [0xE0,0x8D0,0xAD0,0x0,0x38,0x8]
# state = State("ICEY", 0x0264690, bossOffset, playerOffset,
#               [0x190, 0x58, 0x148, 0x10, 0x380, 0xC0])
# print(state.getPlayerPositionX())
