from pymongo import MongoClient
from global_settings import DBHOST
from collections import Counter
import numpy as np
conn = MongoClient(DBHOST, 27027)

collection = conn.billiard['performance500']
cursor = collection.find({})
statistics = []
num_win = 0
while True:
    try:
        rec = cursor.next()
    except:
        break
    num_win += 1
    # if (num_win < 300) or (num_win > 500):
    #     continue
    statistics.append(rec['end'])

len(statistics)
c = Counter(statistics)
c['run out'] / len(statistics)
c

actions = []
collection = conn.billiard['test300']
cursor = collection.find({})
cue_positions = []
cue_object_distance = []
num_win = 0
while True:
    try:
        rec = cursor.next()
    except:
        break
    if rec['t'] == 1:
        continue

    rec['a'][0] -= rec['A']
    r = np.append(rec['a'], rec['pocket'])
    actions.append(r)
    if rec['win']:
        cue_positions.append(rec['st']['Cue_Ball'][0])
        curball = min([
            i for i in rec['st']
            if rec['st'][i][1] > 0.5 and i.startswith('Pool')
        ])
        cue_object_distance.append(
            np.linalg.norm(
                np.array(rec['st']['Cue_Ball'][0]) -
                np.array(rec['st'][curball][0])))
len(actions)
cue_positions = np.array(cue_positions)
cue_object_distance = np.array(cue_object_distance)
actions = np.array(actions)
np.min(actions, 0)
np.savetxt('/home/chenyu/Downloads/actions.csv', actions, delimiter=',')
np.savetxt(
    '/home/chenyu/Downloads/positions.csv', cue_positions, delimiter=',')
np.savetxt(
    '/home/chenyu/Downloads/distances.csv', cue_object_distance, delimiter=',')
