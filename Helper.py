# check whether a game is end
import time
import win32api

from Control import Press


def is_end(next_self_blood, min_hp, next_boss_blood, boss_blood):
    if next_self_blood == 250 and min_hp <= 3:
        return True
    elif next_boss_blood - boss_blood > 400:
        return True
    return False


def Stop():
    if win32api.GetAsyncKeyState(ord("P")):
        return True
    return False


def pause_game(paused):
    op = Stop()
    if op:
        if paused:
            paused = False
            print('start game')
            time.sleep(1)
        else:
            paused = True
            print('pause game')
            time.sleep(1)
    if paused:
        print('paused')
        while True:
            op = Stop()
            # print(op)
            # pauses game and can get annoying.
            if op:
                if paused:
                    paused = False
                    print('start game')
                    time.sleep(1)
                    break
                else:
                    paused = True
                    time.sleep(1)
    return paused


# Stop()
# pause = True
# pause_game(pause)
# get mean score of a reward seq


def mean(d):
    t = 0
    for i in d:
        t += i
    return t / len(d)

# count play hp change, and give reward


def count_self_reward(next_self_blood, self_hp):
    if next_self_blood - self_hp < 0:
        return 11 * (next_self_blood - self_hp)
    return 0

# count boss hp change, and give reward


def count_boss_reward(next_boss_blood, boss_blood):
    if next_boss_blood - boss_blood < 0:
        return int((boss_blood - next_boss_blood)/9)
    return 0


def direction_reward(move, player_x, hornet_x):
    dire = 0
    s = 0
    dis = 0
    base = 5
    if abs(player_x - hornet_x) < 2.5:
        dis = -1
    else:
        dis = 1
    if player_x - hornet_x > 0:
        s = -1
    else:
        s = 1
    if move == 0 or move == 2:
        dire = -1
    else:
        dire = 1

    return dire * s * dis * base


def distance_reward(move, next_player_x, next_hornet_x):
    if abs(next_player_x - next_hornet_x) < 2.5:
        return -6
    elif abs(next_player_x - next_hornet_x) < 4.8:
        return 4
    else:
        if move < 2:
            return 4
        else:
            return -2


def move_judge(self_blood, next_self_blood, player_x, next_player_x, hornet_x, next_hornet_x, move, hornet_skill1):
    # reward = count_self_reward(next_self_blood, self_blood)
    # if reward < 0:
    #     return reward

    if hornet_skill1:
        # run away while distance < 5
        if abs(player_x - hornet_x) < 6:
            # change direction while hornet use skill
            if move == 0 or move == 2:
                dire = 1
            else:
                dire = -1
            if player_x - hornet_x > 0:
                s = -1
            else:
                s = 1
            # if direction is correct and use long move
            if dire * s == 1 and move < 2:
                return 10
        # do not do long move while distance > 5
        else:
            if move >= 2:
                return 10
        return -10

    dis = abs(player_x - hornet_x)
    dire = player_x - hornet_x
    if move == 0:
        if (dis > 5 and dire > 0) or (dis < 2.5 and dire < 0):
            return 10
    elif move == 1:
        if (dis > 5 and dire < 0) or (dis < 2.5 and dire > 0):
            return 10
    elif move == 2:
        if dis > 2.5 and dis < 5 and dire > 0:
            return 10
    elif move == 3:
        if dis > 2.5 and dis < 5 and dire < 0:
            return 10

    # reward = direction_reward(move, player_x, hornet_x) + distance_reward(move, player_x, hornet_x)
    return -10


def act_skill_reward(hornet_skill1, action, next_hornet_x, next_hornet_y, next_player_x):
    skill_reward = 0
    if hornet_skill1:
        if action == 2 or action == 3:
            skill_reward -= 5
    elif next_hornet_y > 34 and abs(next_hornet_x - next_player_x) < 5:
        if action == 4:
            skill_reward += 2
    return skill_reward


def act_distance_reward(action, next_player_x, next_hornet_x, next_hornet_y):
    distance_reward = 0
    if abs(next_player_x - next_hornet_x) < 12:
        if abs(next_player_x - next_hornet_x) > 6:
            if action >= 2 and action <= 3:
                # distance_reward += 0.5
                pass
            elif next_hornet_y < 29 and action == 6:
                distance_reward -= 3
        else:
            if action >= 2 and action <= 3:
                distance_reward -= 0.5
    else:
        if action == 0 and action == 1:
            distance_reward -= 3
        elif action == 6:
            distance_reward += 1
    return distance_reward

# JUDGEMENT FUNCTION, write yourself


def action_judge(boss_blood, next_boss_blood, self_blood,
                 next_self_blood, next_player_x, next_hornet_x, next_hornet_y, action, hornet_skill1):
    # Player dead
    if next_self_blood <= 0 and self_blood != 9:
        skill_reward = act_skill_reward(
            hornet_skill1, action, next_hornet_x, next_hornet_y, next_player_x)
        distance_reward = act_distance_reward(
            action, next_player_x, next_hornet_x, next_hornet_y)
        self_blood_reward = count_self_reward(next_self_blood, self_blood)
        boss_blood_reward = count_boss_reward(next_boss_blood, boss_blood)
        reward = self_blood_reward + boss_blood_reward + distance_reward + skill_reward
        if action == 4:
            reward *= 2
        elif action == 5:
            reward *= 2
        done = 1
        return reward, done
    # boss dead

    elif next_boss_blood <= 0 or next_boss_blood > 900:
        skill_reward = act_skill_reward(
            hornet_skill1, action, next_hornet_x, next_hornet_y, next_player_x)
        distance_reward = act_distance_reward(
            action, next_player_x, next_hornet_x, next_hornet_y)
        self_blood_reward = count_self_reward(next_self_blood, self_blood)
        boss_blood_reward = count_boss_reward(next_boss_blood, boss_blood)
        reward = self_blood_reward + boss_blood_reward + distance_reward + skill_reward
        if action == 4:
            reward *= 2
        elif action == 5:
            reward *= 2
        done = 2
        return reward, done
    # playing
    else:
        skill_reward = act_skill_reward(
            hornet_skill1, action, next_hornet_x, next_hornet_y, next_player_x)
        distance_reward = act_distance_reward(
            action, next_player_x, next_hornet_x, next_hornet_y)
        self_blood_reward = count_self_reward(next_self_blood, self_blood)
        boss_blood_reward = count_boss_reward(next_boss_blood, boss_blood)

        reward = self_blood_reward + boss_blood_reward + distance_reward + skill_reward
        if action == 4:
            reward *= 2
        elif action == 5:
            reward *= 2
        done = 0
        return reward, done


def actionEvaluate(playerHp, bossHp, nextPlayerHp, nextBossHp, action):
    rewardBoss = bossHp - nextBossHp
    rewardPlayer = 10 * (nextPlayerHp - playerHp)
    rewardSkill = skillReward(
        playerHp, bossHp, nextPlayerHp, nextBossHp, action)
    reward = rewardBoss + rewardPlayer + rewardSkill
    # 玩家死了
    if nextPlayerHp <= 0:
        done = 1
        return reward, done
    # Boss 死了
    elif nextBossHp <= 0:
        done = 2
        return reward, done
    # 游戏中
    else:
        done = 0
        return reward, done


def skillReward(playerHp, bossHp, nextPlayerHp, nextBossHp, action):
    # 如果使用了技能 判断是否造成伤害 如果没造成伤害 加大惩罚力度 如果造成了伤害减少惩罚力度 增加奖励力度
    if action == 4 or action == 5:
        if bossHp - nextBossHp == 0:
            return 20 * (nextPlayerHp-playerHp)
        else:
            return 10 * (bossHp-nextBossHp)
    else:
        return 0


def moveEvaluate(playerHp, bossHp, nextPlayerHp, nextBossHp, action, playerX, bossX):
    rewardBoss = bossHp - nextBossHp
    rewardPlayer = 10 * (nextPlayerHp - playerHp)
    rewardDist = 0
    # 不能距离 BOSS 太远或太近
    # 太远
    if abs(bossX - playerX) > 8:
        rewardDist = -(abs(bossX - playerX) - 8) * 10
    # 太近
    if abs(playerX-bossX) < 2:
        rewardDist = -abs(bossX - playerX) * 30
    reward = rewardBoss + rewardPlayer + rewardDist
    return reward
