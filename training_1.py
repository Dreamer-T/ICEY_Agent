# -*- coding: utf-8 -*-
import numpy as np
from tensorflow.keras.models import load_model
import tensorflow as tf
import os
import cv2
import time
import collections
import matplotlib.pyplot as plt
from Control import KeyDown, KeyUp, Press

from Model import Model
from DQN import DQN
from Agent import Agent
from ReplayMemory import ReplayMemory


import Helper
import Actions
from Helper import mean, is_end
from Actions import A, takeAction, restart, takeMove, TackAction
from GetScreen import getScreen
# from GetHp import State
from Frame import Frame
from State import State
# window_size = (0, 0, 1920, 1017)
# station_size = (230, 230, 1670, 930)

WIDTH = 384
HEIGHT = 216
ACTION_TYPES = 7
BUFFER_SIZE = 4
INPUT_SHAPE = (BUFFER_SIZE, HEIGHT, WIDTH, 3)

MEMORY_SIZE = 200  # replay memory的大小
MEMORY_WARMUP_SIZE = 24  # replay_memory 里需要预存一些经验数据，再从里面取样让AI学习
BATCH_SIZE = 10  # 每次给agent learn的数据数量，从replay memory随机里取样
ALPHA = 0.001  # 学习率
GAMMA = 0


DELAY_REWARD = 1


def training(state: State, algorithm: DQN, agent: Agent,
             actionReplayMemory: ReplayMemory, moveReplayMemory: ReplayMemory, PASS_COUNT, paused):
    restart()
    # 游戏开始预热学习
    for i in range(8):
        if (len(moveReplayMemory) > MEMORY_WARMUP_SIZE):
            # print("move learning")
            batch_station, batch_actions, batch_reward, batch_next_station, batch_done = moveReplayMemory.sample(
                BATCH_SIZE)
            algorithm.move_learn(batch_station, batch_actions,
                                 batch_reward, batch_next_station, batch_done)

        if (len(actionReplayMemory) > MEMORY_WARMUP_SIZE):
            # print("action learning")
            batch_station, batch_actions, batch_reward, batch_next_station, batch_done = actionReplayMemory.sample(
                BATCH_SIZE)
            algorithm.actionLearn(batch_station, batch_actions,
                                  batch_reward, batch_next_station, batch_done)

    step = 0
    done = 0
    totalReward = 0

    # 奖励
    delayMoveReward = collections.deque(maxlen=DELAY_REWARD)
    delayActReward = collections.deque(maxlen=DELAY_REWARD)
    delayStation = collections.deque(
        maxlen=DELAY_REWARD + 1)
    delayActions = collections.deque(maxlen=DELAY_REWARD)
    delayDirection = collections.deque(maxlen=DELAY_REWARD)

    # 面对BOSS
    KeyDown(A)
    time.sleep(2)
    KeyUp(A)

    # 开始储存图像
    thread1 = Frame(1, "Frame", WIDTH,
                    HEIGHT, maxlen=BUFFER_SIZE)
    thread1.start()
    # 游戏开始
    while True:
        step += 1
        while(len(thread1.buffer) < BUFFER_SIZE):
            time.sleep(0.1)

        stations = thread1.getBuffer()
        bossHp = state.getBossHp()
        playerHp = state.getPlayerHp()
        playerX = state.getPlayerPositionX()
        bossX = state.getBossX()
        # 根据游戏场景做出反应
        move, action = agent.sample(stations, playerHp, bossHp, playerX, bossX)

        takeMove(move)
        takeAction(action)

        nextStation = thread1.getBuffer()
        nextBossHp = state.getBossHp()
        nextPlayerHp = state.getPlayerHp()
        playerX = state.getPlayerPositionX()
        bossX = state.getBossX()

        # 建立反馈（奖励/惩罚）
        moveReward = Helper.moveEvaluate(
            playerHp, bossHp, nextPlayerHp, nextBossHp, move, playerX, bossX)
        actionReward, done = Helper.actionEvaluate(
            playerHp, bossHp, nextPlayerHp, nextBossHp, action)

        # 添加到奖励池
        delayMoveReward.append(moveReward)
        delayActReward.append(actionReward)
        delayStation.append(stations)
        delayActions.append(action)
        delayDirection.append(move)

        if len(delayStation) >= DELAY_REWARD + 1:
            if delayMoveReward[0] != 0:
                moveReplayMemory.append(
                    (delayStation[0], delayDirection[0], delayMoveReward[0], delayStation[1], done))

        if len(delayStation) >= DELAY_REWARD + 1:
            if mean(delayActReward) != 0:
                actionReplayMemory.append((delayStation[0], delayActions[0], mean(
                    delayActReward), delayStation[1], done))

        station = nextStation
        playerHp = nextPlayerHp
        bossHp = nextBossHp

        totalReward += actionReward
        paused = Helper.pause_game(paused)
        # print(done,playerHp,bossHp)AIAIAIAIAIAIAIAIALAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAI
        if done == 1:

            Actions.Nothing()
            break
        elif done == 2:
            PASS_COUNT += 1
            Actions.Nothing()
            time.sleep(3)
            break

    thread1.stop()

    # 开始学习
    for i in range(8):
        if (len(moveReplayMemory) > MEMORY_WARMUP_SIZE):
            batch_station, batch_actions, batch_reward, batch_next_station, batch_done = moveReplayMemory.sample(
                BATCH_SIZE)
            algorithm.move_learn(batch_station, batch_actions,
                                 batch_reward, batch_next_station, batch_done)

        if (len(actionReplayMemory) > MEMORY_WARMUP_SIZE):
            batch_station, batch_actions, batch_reward, batch_next_station, batch_done = actionReplayMemory.sample(
                BATCH_SIZE)
            algorithm.actionLearn(batch_station, batch_actions,
                                  batch_reward, batch_next_station, batch_done)

    return totalReward, step, PASS_COUNT, playerHp, bossHp


if __name__ == '__main__':

    config = tf.compat.v1.ConfigProto(allow_soft_placement=True)
    config.gpu_options.allow_growth = True  # 程序按需申请内存
    sess = tf.compat.v1.Session(config=config)

    totalRemindHp = 0
    totalBossRemindHp = 0
    totalReward = 0

    actionReplayMemory = ReplayMemory(
        MEMORY_SIZE, fileName='./act_memory')         # experience pool
    moveReplayMemory = ReplayMemory(
        MEMORY_SIZE, fileName='./move_memory')         # experience pool

    # new model, if exit save file, load it
    model = Model(INPUT_SHAPE, ACTION_TYPES)

    playerHpOffset = [0x88, 0xA8, 0x58, 0x18, 0x28, 0x20]
    bossHpOffset = [0x190, 0x58, 0x3D8, 0x0, 0xA8, 0x0, 0x94]
    playerXOffset = [0x280, 0x130, 0x18, 0x18, 0x38, 0x8]
    playerYOffset = [0x58, 0x50, 0x50, 0x0, 0x40, 0xC0]
    bossXOffset = [0xA60, 0xE08, 0xD8, 0x360, 0x60, 0x2C]
    state = State("ICEY", 0x1349318, 0x0264690, 0x1346B08, 0x12ECBD0, 0x1294728, bossHpOffset, playerHpOffset, playerXOffset,
                  playerYOffset, bossXOffset)
    model.load_model()
    algorithm = DQN(model, gamma=GAMMA, learnging_rate=ALPHA)
    agent = Agent(ACTION_TYPES, algorithm, eGreed=0.12, eGreedDecrease=1e-6)
    print(state.getPlayerPositionX())
    # paused at the begining
    paused = True
    paused = Helper.pause_game(paused)

    EPISODE = 280
    # 开始训练
    episode = 0
    PASS_COUNT = 0
    with open("log.txt", "a") as log:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        log.write(now + "\n")
    while episode < EPISODE:    # 训练max_episode个回合，test部分不计算入episode数量
        # 训练
        episode += 1

        currentReward, totalStep, PASS_COUNT, remindHp, bossRemindHp = training(
            state, algorithm, agent, actionReplayMemory, moveReplayMemory, PASS_COUNT, paused)
        if episode % 10 == 5:
            model.save_model()
        if episode % 10 == 0:
            moveReplayMemory.save(moveReplayMemory.fileName)
        if episode % 10 == 0:
            actionReplayMemory.save(actionReplayMemory.fileName)
        totalRemindHp += remindHp
        totalBossRemindHp += bossRemindHp
        totalReward += currentReward
        with open("log.txt", "a") as log:
            string = "Episode: " + str(episode) + ", pass_count: " + \
                str(PASS_COUNT) + ", playerHp:" + str(totalRemindHp / episode) +\
                ",bossHp:" + str(totalBossRemindHp / episode) +\
                ",currentReward:" + str(currentReward) +\
                ",averageReward:" + str(totalReward / episode) + "\n"
            log.write(string)
    with open("log.txt", "a") as log:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        log.write(now + "\n\n")
    time.sleep(5)
    os.system("taskkill /pid " + str(state.pid))
    os.system("shutdown -s -t 10")
