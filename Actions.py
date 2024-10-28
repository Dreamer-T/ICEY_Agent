# Define the actions we may need during training
# You can define your actions here

from grpc import dynamic_ssl_server_credentials
from Control import KeyDown, KeyUp, Press
from GetScreen import getScreen
import time
import cv2
import threading

# Hash code for key we may use: https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes?redirectedfrom=MSDN


W = 0x11
A = 0x1E
S = 0x1F
D = 0x20


J = 0x24
K = 0x25
I = 0x17
O = 0x18
N = 0x31
U = 0x16
L = 0x26
SPACE = 0x39
ENTER = 0x1c
ESC = 0x01


# 移动
# 0
def MoveLeft():
    KeyDown(A)
    time.sleep(0.01)


# 1
def MoveRight():
    KeyDown(D)
    time.sleep(0.01)


# 2
def TurnLeft():
    Nothing()
    Press(A)


# 3
def TurnRight():
    Nothing()
    Press(D)


# 动作
# 0
def Attack():
    Press(J)
    time.sleep(0.01)


# 1
def Hit():
    Press(I)
    time.sleep(0.01)


# 2
def Jump():
    Press(SPACE)
    time.sleep(0.01)


# 3
def Dash():
    Press(O)
    time.sleep(0.1)


# 4
def Skill0():
    Press(K)
    time.sleep(0.01)


# 5
def Skill1():
    Press(N)
    time.sleep(0.01)


# 6
def Critical():
    Press(U)
    time.sleep(0.01)


# 7
def Specail():
    Press(L)
    time.sleep(0.01)


# 8
def Nothing():
    KeyUp(A)
    KeyUp(D)
    pass


def restart():
    time.sleep(3)
    KeyDown(D)
    time.sleep(1)
    KeyUp(D)
    Press(ENTER)
    time.sleep(3)
    Press(ESC)
    for i in range(2):
        Press(S)
    Press(ENTER)
    time.sleep(8)
    Press(D)
    for i in range(3):
        Press(S)
    Press(ENTER)
    time.sleep(2)
    KeyDown(D)
    time.sleep(8)
    for i in range(6):
        Press(O)
        time.sleep(0.1)
    time.sleep(1)
    Press(A)
    for i in range(5):
        Press(O)
        time.sleep(0.1)
    time.sleep(1)
    for i in range(4):
        Press(O)
        time.sleep(0.1)
    time.sleep(3)
    KeyDown(A)
    time.sleep(10)
    KeyUp(A)
    pass


# List for action functions
Actions = [Attack, Hit,
           Jump, Specail,
           Skill0, Skill1, Critical]
Directions = [MoveLeft, MoveRight, TurnLeft, TurnRight, Dash]
# Run the action


def takeAction(action):
    Actions[action]()


def takeMove(direc):
    Directions[direc]()


class TackAction(threading.Thread):
    def __init__(self, threadID, name, direction, action):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.direction = direction
        self.action = action

    def run(self):
        takeMove(self.direction)
        takeAction(self.action)


# restart()
