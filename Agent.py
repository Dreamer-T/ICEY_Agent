import numpy as np

from DQN import DQN


class Agent:
    def __init__(self, actionTypes, algorithm: DQN, eGreed=0.1, eGreedDecrease=0):
        self.actionTypes = actionTypes
        self.algorithm = algorithm
        self.eGreed = eGreed
        self.eGreedDecrease = eGreedDecrease

    def sample(self, station, playerHp, bossHp, playerX, bossX):

        movePrediction, actionPrediction = self.algorithm.model.predict(
            station)
        movePrediction = movePrediction.numpy()
        actionPrediction = actionPrediction.numpy()
        # 生成随机数
        x = np.random.rand()
        if x < self.eGreed:
            # 随机方向（探索）
            move = np.random.randint(5)
            move = self.betterMove(playerX, bossX, move)
        else:
            move = np.argmax(movePrediction)
        self.eGreed = max(
            0.03, self.eGreed - self.eGreedDecrease)

        # 生成随机数
        x = np.random.rand()
        if x < self.eGreed:
            # 随机动作（探索）
            act = np.random.randint(self.actionTypes)
            act = self.betterAction(playerHp, bossHp, act)
        else:
            # 根据经验（开发）
            act = np.argmax(actionPrediction)
            # 血量低不鼓励使用技能
            if playerHp <= 50:
                if act == 4 or act == 5:
                    actionPrediction[0][4] = -100
                    actionPrediction[0][5] = -100
            act = np.argmax(actionPrediction)

        self.eGreed = max(
            0.03, self.eGreed - self.eGreedDecrease)
        return move, act

    #  探索时 80%面向BOSS 20%不改变 面向BOSS的策略有两种：转向和移动

    def betterMove(self, playerX, bossX, move):
        r = np.random.rand()
        if r > 0.8:
            return move
        if bossX > playerX:
            x = np.random.rand()
            if x < 0.5:
                return 3
            if x > 0.5:
                return 1
        if bossX < playerX:
            x = np.random.rand()
            if x < 0.5:
                return 2
            if x > 0.5:
                return 0

    def betterAction(self, playerHp, bossHp, act):
        # 血量低（50）不鼓励使用技能
        if playerHp <= 50:
            if act == 5 or act == 4:
                act = 0
        # 处决
        if bossHp <= 2500 and bossHp >= 2280:
            return 3
        if bossHp <= 210:
            return 3
        return act
