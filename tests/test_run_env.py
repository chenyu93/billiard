from billiard_env.pool_env import Env
import random
from tqdm import tqdm
Env.set_speed(999)

for _ in tqdm(range(100)):
    Env.reset()
    Env.act(angle=0.0, v_cue=1.0 + random.random())
