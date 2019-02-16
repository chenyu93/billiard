import itertools
import sys
import math
from multiprocessing.dummy import Pool as ThreadPool
import tensorflow as tf
import numpy as np
import copy
from pymongo import MongoClient
from zmqlib import ClientTask
from global_settings import DBHOST, TRAIN_NPSIZE, TRAIN_REPEATEPOCH, TRAIN_BATCHSIZE, NUM_FEATURE

# pylint: disable-msg=C0103, C0111, E1101


def equalweights(step, reward):
    return 1.0


def gamma95(step, reward):
    return math.pow(.95, step) * reward // 10


def get_db(collection, makeweights, maxsize=1e10):

    num = 0
    conn = MongoClient(DBHOST, 27027)
    collection = conn.billiard[collection]
    cursor = collection.find({})
    state, action, value, pockets = [], [], [], []
    while True:
        try:
            rec = cursor.next()
            if not rec['st']:
                continue
            num += 1
            if num > maxsize:
                break
        except:
            break
        if rec['a'] is None:
            continue

        rec['a'][0] -= rec['A']
        rec['a'][0] = np.clip(rec['a'][0], -3, 3)
        rec['a'][0] = rec['a'][0] / 3.0
        # CamRotation, v_cue, cue_angle, top_back_spin, left_right_spin
        rec['a'][1] = rec['a'][1] / 40.0
        rec['a'][2] = rec['a'][2] / 10.0
        rec['a'][3] = rec['a'][3] / 50.0
        rec['a'][4] = rec['a'][4] / 50.0
        state.append(rec['st'])
        action.append(rec['a'])
        if rec['result']:
            value.append(1)
        elif rec['max_t'] == rec['t']:
            value.append(-1)
        else:
            value.append((rec['max_t'] - rec['t']) / 8.0)
        pockets.append(rec['pocket'])

        ast = copy.deepcopy(rec['st'])
        aac = copy.deepcopy(rec['a'])
        ava = copy.deepcopy(rec['result'])
        apo = copy.deepcopy(rec['pocket'])
        for each in ast:
            ast[each][0][0] = -ast[each][0][0]
        aac[0] = -aac[0]
        aac[-1] = -aac[-1]
        if apo % 2 == 0:
            apo += 1
        else:
            apo -= 1
        state.append(ast)
        action.append(aac)
        value.append(ava)
        pockets.append(apo)
    return state, action, value, pockets


def consume_batch(args):
    """
    """
    threadid, pocket, batch = args
    client = ClientTask()
    client.build_feature_socket('sample_memory_{}'.format(threadid))
    result = []
    for p, each in zip(pocket, batch):
        result.append(client.ask_feature((p, each)))
    return result


def get_test_input_fn(collection, test_data_size):
    batchsize = 100
    state, action, value, pockets = get_db(
        collection, equalweights, maxsize=test_data_size)

    jobs = [(i + 1000 * ('test' in collection),
             pockets[(batchsize * i):(batchsize * (i + 1))],
             state[(batchsize * i):(batchsize * (i + 1))])
            for i in range(len(state) // batchsize + 1)]
    pool = ThreadPool(40)
    results = pool.map(consume_batch, jobs)
    btensor = list(itertools.chain(*results))
    input_tpye = {'X': np.array(btensor, dtype=np.float16)}

    y = np.array(
        [([v] + a) for (v, a) in zip(value, action)], dtype=np.float32)
    del pool
    return tf.estimator.inputs.numpy_input_fn(
        x=input_tpye,
        y=y,
        batch_size=TRAIN_BATCHSIZE,
        shuffle=False,
        num_epochs=1)


def np_to_queue(collection, queue):
    state, action, value, pockets = get_db(collection, equalweights)

    screen = 0
    batchsize = TRAIN_NPSIZE // 100
    pool = ThreadPool(40)
    while True:
        bstate = state[screen:(screen + TRAIN_NPSIZE)]
        baction = action[screen:(screen + TRAIN_NPSIZE)]
        bvalue = value[screen:(screen + TRAIN_NPSIZE)]
        bpockets = pockets[screen:(screen + TRAIN_NPSIZE)]
        jobs = [(i + 1000 * ('test' in collection),
                 bpockets[(batchsize * i):(batchsize * (i + 1))],
                 bstate[(batchsize * i):(batchsize * (i + 1))])
                for i in range(101)]
        print('len jobs', len(jobs))
        results = pool.map(consume_batch, jobs)
        print(
            'finish rendering', collection, len(results), TRAIN_NPSIZE, end='')
        btensor = list(itertools.chain(*results))
        print('btensor ', len(btensor), 'bvalue', len(bvalue))
        screen += TRAIN_NPSIZE
        if screen + TRAIN_NPSIZE > len(state):
            screen = 0
        input_tpye = {'X': np.array(btensor, dtype=np.float16)}
        y = np.array(
            [([v] + a) for (v, a) in zip(bvalue, baction)], dtype=np.float32)

        input_fn = tf.estimator.inputs.numpy_input_fn(
            x=input_tpye,
            y=y,
            batch_size=TRAIN_BATCHSIZE,
            shuffle='train' in collection,
            num_epochs=TRAIN_REPEATEPOCH)
        queue.put(input_fn)
        print('queuesize', queue.qsize())


if __name__ == '__main__':
    state, action, value, pockets = get_db('train300', equalweights)
    collection = 'train300'
