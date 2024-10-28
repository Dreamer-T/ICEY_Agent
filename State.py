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
    def __init__(self, gameName: str, basePlayerHp, baseBossHp, basePlayerX, basePlayerY, baseBossX,
                 bossHpOffset: list, playerHpOffset: list, playerXOffset: list, playerYOffset: list,
                 bossXOffset: list) -> None:
        """
        gameName 表示游戏窗口所显示的名字用以获得游戏进程号

        base 项皆为基于 gameName.exe 的基础偏移量

        offset 项皆为偏移地址列表
        """
        self.bossHpOffset = bossHpOffset
        self.playerHpOffset = playerHpOffset
        self.playerXOffset = playerXOffset
        self.playerYOffset = playerYOffset
        self.bossXOffset = bossXOffset
        hd = win32gui.FindWindow(None, gameName)
        pid = win32process.GetWindowThreadProcessId(hd)[1]
        self.pid = pid
        k32 = c.windll.LoadLibrary("C:\\Windows\\System32\\kernel32.dll")
        self.process_handle = win32api.OpenProcess(0x1F0FFF, False, pid)
        tempL = len(gameName)
        # get dll address
        hProcess = k32.OpenProcess(
            PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
            False, pid)
        hModule = EnumProcessModulesEx(hProcess)
        for i in hModule:
            temp = win32process.GetModuleFileNameEx(
                self.process_handle, i.value)
            if temp[-(tempL + 4):] == gameName + ".exe":
                self.playerExe = i.value + basePlayerHp
                self.playerXExe = i.value + basePlayerX
                self.playerYExe = i.value + basePlayerY
                self.bossXExe = i.value + baseBossX

            if temp[-8:] == "mono.dll":
                self.bossExe = i.value + baseBossHp
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

    def getPlayerPositionX(self):
        data = c.c_ulonglong()
        bytesRead = c.c_ulonglong()
        self.ReadProcessMemory(self.processHandle, self.playerXExe, c.byref(
            data), c.sizeof(data), c.byref(bytesRead))
        offsets = self.playerXOffset[0:-1]
        for num in offsets:
            self.ReadProcessMemory(self.processHandle, data.value + num, c.byref(
                data), c.sizeof(data), c.byref(bytesRead))
        x = c.c_float()
        self.ReadProcessMemory(
            self.processHandle, data.value + self.playerXOffset[-1], c.byref(x), c.sizeof(data), c.byref(bytesRead))
        return x.value

    def getPlayerPositionY(self):
        data = c.c_ulonglong()
        bytesRead = c.c_ulonglong()
        self.ReadProcessMemory(self.processHandle, self.playerYExe, c.byref(
            data), c.sizeof(data), c.byref(bytesRead))
        offsets = self.playerYOffset[0:-1]
        for num in offsets:
            self.ReadProcessMemory(self.processHandle, data.value + num, c.byref(
                data), c.sizeof(data), c.byref(bytesRead))
        y = c.c_float()
        self.ReadProcessMemory(
            self.processHandle, data.value + self.playerYOffset[-1], c.byref(y), c.sizeof(data), c.byref(bytesRead))
        return y.value

    def getPlayerPostion(self):
        x = self.getPlayerPositionX()
        y = self.getPlayerPositionY()
        return x, y

    def getPlayerHp(self) -> int:
        """
        获取玩家血量
        """
        data = c.c_ulonglong()
        bytesRead = c.c_ulonglong()
        self.ReadProcessMemory(self.processHandle, self.playerExe, c.byref(
            data), c.sizeof(data), c.byref(bytesRead))
        for num in self.playerHpOffset:
            self.ReadProcessMemory(self.processHandle, data.value + num, c.byref(
                data), c.sizeof(data), c.byref(bytesRead))
        a = '{:016X}'.format(data.value)
        hpx = a[-2:]
        return int(hpx, 16)

    def getBossHp(self) -> int:
        """
        获取游戏内BOSS血量
        """
        data = c.c_ulonglong()
        bytesRead = c.c_ulonglong()
        self.ReadProcessMemory(self.processHandle, self.bossExe, c.byref(
            data), c.sizeof(data), c.byref(bytesRead))
        for num in self.bossHpOffset:
            self.ReadProcessMemory(self.processHandle, data.value + num, c.byref(
                data), c.sizeof(data), c.byref(bytesRead))
        a = '{:016X}'.format(data.value)
        hpx = a
        return int(hpx, 16)

    def getBossX(self):
        data = c.c_ulonglong()
        bytesRead = c.c_ulonglong()
        self.ReadProcessMemory(self.processHandle, self.bossXExe, c.byref(
            data), c.sizeof(data), c.byref(bytesRead))
        offsets = self.bossXOffset[0:-1]
        for num in offsets:
            self.ReadProcessMemory(self.processHandle, data.value + num, c.byref(
                data), c.sizeof(data), c.byref(bytesRead))
        x = c.c_float()
        self.ReadProcessMemory(
            self.processHandle, data.value + self.bossXOffset[-1], c.byref(x), c.sizeof(data), c.byref(bytesRead))
        return x.value


# # PLAYER_X-ICEY
# # 0x12957A0 [0x60, 0x40, 0x1E8, 0x58, 0x678, 0x8]
# # 0x1355BD0 [10 130 18 18 38 8]
# # 0x1346B08 [280 130 18 18 38 8]

# # PLAYER_Y-ICEY
# # 0x12ECBD0 [0x58, 0x50, 0x50, 0x0, 0x40, 0xC0]

# # PLAYER_HP-ICEY
# # 0x1349318 [0x88, 0xA8, 0x58, 0x18, 0x28, 0x20]

# # BOSS_HP-ICEY
# # 0x10F974C [0xB4, 0x18, 0x10, 0x94]
# # 0x10F3A84 [0xB4, 0x18, 0x10, 0x28, 0x80, 0x94]

# # BOSS_X-ICEY
# # 0x1294728 [0xA60, 0xE08, 0xD8, 0x360, 0x60, 0x2C]
# # 0x1296FF0 [0x1D8, 0x800, 0xC88, 0xFD8, 0x120, 0x2C]
