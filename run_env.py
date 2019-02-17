from pool_env import Env


Env.set_speed(0.032)

state = Env.get_state()
Env.act(angle=0.0, v_cue=2.0, gif_filename='test.gif')
Env.plot_table('test.jpg')
