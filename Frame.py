import threading
import time
import collections
import cv2
import win32gui
import win32ui
import win32con
import win32api
import numpy as np
import tensorflow as tf
from GetScreen import getScreen


class Frame(threading.Thread):
    def __init__(self, threadID, name, width, height,  maxlen=5):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.buffer = collections.deque(maxlen=maxlen)
        self.lock = threading.Lock()

        self.WIDTH = width
        self.HEIGHT = height
        self._stop_event = threading.Event()

    def run(self):
        while not self.stopped():
            self.getFrame()
            time.sleep(0.05)

    def getFrame(self):
        self.lock.acquire(blocking=True)
        station = cv2.resize(cv2.cvtColor(
            getScreen(), cv2.COLOR_RGBA2RGB), (self.WIDTH, self.HEIGHT))
        self.buffer.append(tf.convert_to_tensor(station))
        self.lock.release()

    def getBuffer(self):
        buffer = []
        self.lock.acquire(blocking=True)
        for f in self.buffer:
            buffer.append(f)
        self.lock.release()
        return buffer

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


# WIDTH = 400
# HEIGHT = 200
# FRAMEBUFFERSIZE = 4
# thread1 = Frame(1, "Frame", WIDTH,
#                 HEIGHT, maxlen=FRAMEBUFFERSIZE)
# thread1.start()
# listone = thread1.getBuffer()
# print(listone[0].shape)
