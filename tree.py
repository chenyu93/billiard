"""Tree search for each shoot.

A monte carlo tree.
simulate on the first step, get st+1, legal path check on the second step.

data structure:
{
    a_i :[(a_i + delta, st', real_success, V(st'), theoritical_available(st'))]

}

CamRotation, v_cue, cue_angle, top_back_spin, left_right_spin
"""

# pylint: disable-msg=C0103, C0111

import random
import copy
import numpy as np
from services.action import prior_speed
from global_settings import ALPHA1, ALPHA2, ALPHA5, ALPHA6, MODEL_VERSION
from zmqlib import Push
display = True


class Item(object):
    def __init__(self, st, A, a):
        self.A = A * 1
        self.a = a * 1
        self.st = copy.deepcopy(st)
        self.st1 = None
        self.bravo = None
        self.maxQst1 = 0

    def update_result(self, st1, bravo, Qsa_set):
        self.st1 = copy.deepcopy(st1)
        self.bravo = bravo
        if self.bravo:
            self.maxQst1 = max([i[3] for i in Qsa_set])


class TreeStruct(object):
    """tree for shoot."""

    def __init__(self, dict_state, object_ball, Qsa_set):
        self.dict_state = dict_state
        self.object_ball = object_ball
        self.Qsa_set = Qsa_set
        self.macro_set = [i[0] for i in Qsa_set]
        self.success_exp = dict([(i[0], []) for i in Qsa_set])
        self.callpockets = dict([(i[0], i[1]) for i in Qsa_set])
        self.Qt = dict((i[0], i[2]) for i in Qsa_set)
        self.nodes = dict((i[0], []) for i in Qsa_set)
        self.micro_set = dict((i[0], i[3:]) for i in Qsa_set)
        self.N = 0
        self.last_A = None
        self.num_bravo = 0
        self.v_star = -999
        self.l_star = -1
        self.ready = False
        if display:
            self.sock = Push()
            self.sock.build_record_socket()

    # def aim_search_ready(self):
    #     return (self.N >= AIM_STEPS) or (self.num_bravo >= AIM_SUCCESS)

    @classmethod
    def initial_shoot(cls):
        #pylint: disable-msg=E1101
        a = [
            np.random.uniform(low=-0.15, high=0.15),
            np.random.uniform(low=33, high=45), 0,
            np.clip(np.random.normal(0, 5), -40, 40),
            np.clip(np.random.normal(0, 25), -40, 40)
        ]
        return a

    def self_play(self):
        angles = list(self.nodes.keys())
        Q1 = []
        for each in angles:
            if self.nodes[each]:
                Q1.append(max([i.maxQst1 for i in self.nodes[each]]))
            else:
                Q1.append(0)
        ind_A = np.argmax([(ALPHA2 * i + (1 - ALPHA2) * self.Qt[j])
                           for i, j in zip(Q1, self.Qt)])
        A = angles[ind_A]
        callpocket = self.callpockets[A]
        if not self.nodes[A]:
            return 'GAMEOVER', 'GAMEOVER', 'GAMEOVER'
        ind_a = np.argmax([i.maxQst1 for i in self.nodes[A]])
        item = self.nodes[A][ind_a]
        self.v_star = -999
        self.l_star = -1
        self.ready = False
        if item.maxQst1 <= 0:
            return 'GAMEOVER', 'GAMEOVER', 'GAMEOVER'
        return A, item.a, callpocket

    def macro_search(self):
        angles = list(self.nodes.keys())
        if len(angles) == 0:
            return 'GAMEOVER', 'GAMEOVER'
        Q1 = []
        for each in angles:
            if self.nodes[each]:
                Q1.append(max(i.maxQst1 for i in self.nodes[each]))
            else:
                Q1.append(0)
        N = [len(self.nodes[each]) + 1 for each in angles]
        U = [self.N / np.sqrt(i) for i in N]
        a = np.argmax([(ALPHA1 * i + (1 - ALPHA1) * j) for i, j in zip(Q1, U)])
        A = angles[a]
        callpocket = self.callpockets[A]
        # print('|' * 60)
        # print(self.N, self.num_bravo, self.l_star, self.v_star, self.ready)
        # for i, j, k, l in zip(angles, Q1, U, N):
        #     print('%3f\t%3f\t%3f\t%d' % (i, j, k, l))

        return A, callpocket

    #pylint: disable-msg=E1101
    def explore(self, A, a):

        # a + delta
        # CamRotation, v_cue, cue_angle, top_back_spin, left_right_spin

        if (self.success_exp[A]) and (random.random() < 0.8):
            a = copy.deepcopy(self.success_exp[A][0])
            a[0] += np.random.normal(0, 0.01 * (self.N // 50 + 1))
            a[1] += np.random.uniform(low=-10, high=10)
            a[2] += np.random.uniform(low=-10, high=10)
            a[3] = np.random.uniform(low=-25, high=25)
            a[4] = np.random.uniform(low=-25, high=25)
        else:
            a[0] = np.random.normal(0, 0.1 * (self.N // 50 + 1))
            if MODEL_VERSION <= 500:
                a[1] = np.random.uniform(low=15, high=35)
            else:
                a[1] += np.random.uniform(low=-15, high=15)
            a[2] = np.random.uniform(low=-30, high=30)
            a[3] = np.random.uniform(low=-20, high=20)
            a[4] = np.random.uniform(low=-20, high=20)
        a[1] = np.clip(a[1], 5, 40)
        a[2] = np.clip(a[2], -10, 10)
        a[3] = np.clip(a[3], -50, 50)
        a[4] = np.clip(a[4], -50, 50)
        return a

    def search(self):
        if self.ready:
            # the last aim, or GAMEOVER
            A, a, callpocket = self.self_play()
            return A, a, callpocket
        A, callpocket = self.macro_search()
        if A == 'GAMEOVER':
            return 'GAMEOVER', 'GAMEOVER', 'GAMEOVER'
        a = self.micro_set[A] * 1
        a = self.explore(A, a)
        self.nodes[A].append(Item(self.dict_state, A, a))
        self.last_A = A
        return A, a, callpocket

    def update(self, st1, bravo, success, Qsa_set):
        self.nodes[self.last_A][-1].update_result(st1, bravo, Qsa_set)
        self.N += 1
        if self.nodes[self.last_A][-1].bravo:
            self.num_bravo += 1
        if Qsa_set:
            v = max([i[3] for i in Qsa_set])
        else:
            v = -9999

        if (v > self.v_star) and (v > 0.0001):
            if (v - self.v_star) / (self.N - self.l_star) > ALPHA5:
                self.v_star = v
                self.l_star = self.N
            elif self.N > ALPHA6:
                self.ready = True
        else:
            if self.N - self.l_star > ALPHA6:
                self.ready = True
        if success:
            self.success_exp[self.last_A].append(self.nodes[self.last_A][-1].a)
        #######  FOR MCTS
        if (MODEL_VERSION >= 300) and (MODEL_VERSION < 400):
            if bravo:
                self.ready = True
        if display:
            allballs = [
                i for i in self.dict_state
                if (self.dict_state[i][1] > 0.5) and i.startswith('P')
            ]
            allballs = sorted(allballs)
            stats = [self.v_star, v, self.l_star, self.N]
            actions = self.nodes[self.last_A][-1].a
            pocket = self.callpockets[self.last_A]
            if len(allballs) > 1:
                x = 1
            else:
                x = 0
            self.sock.send_record((allballs[0], allballs[x], self.last_A,
                                   actions, stats, pocket))
        #######  FOR MCTS
