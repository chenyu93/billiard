from billiard_env.pool_env import Env

Env.set_speed(0.032)   # 1 / 0.0032 = 31.25 fps
state = Env.get_state()
Env.act(angle=0.0, v_cue=2.0, gif_filename='test.gif')
Env.plot_table('test.jpg')
