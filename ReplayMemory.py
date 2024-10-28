import random
import collections
import numpy as np
import pickle
import os


class ReplayMemory:
    def __init__(self, size, fileName):
        self.size = size
        self.count = 0
        self.fileName = fileName
        self.buffer = collections.deque(maxlen=size)

    def append(self, exp):
        self.count += 1
        self.buffer.append(exp)

    def sample(self, batchSize):
        # random batch
        mini_batch = random.sample(self.buffer, batchSize)

        observation, action, reward, nextObservation, finish = [], [], [], [], []

        for experience in mini_batch:
            s, a, r, s_p, done = experience
            observation.append(s)
            action.append(a)
            reward.append(r)
            nextObservation.append(s_p)
            finish.append(done)

        return np.array(observation).astype('float32'), \
            np.array(action).astype('int32'), np.array(reward).astype('float32'),\
            np.array(nextObservation).astype('float32'), np.array(
                finish).astype('float32')

    def save(self, fileName):
        count = 0
        for x in os.listdir(fileName):
            count += 1
        fileName = fileName + "/memory_" + str(count) + ".txt"
        pickle.dump(self.buffer, open(fileName, 'wb'))
        print("Save memory:", fileName)

    def load(self, fileName):
        self.buffer = pickle.load(open(fileName, 'rb'))
        return self.buffer

    def __len__(self):
        return len(self.buffer)
