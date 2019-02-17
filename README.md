billiard

# Install


## firsttime install
```bash
pip install shapely msgpack_numpy pi3d

cd speed
python setup.py build_ext -i
```


## test speed script
```bash
python -m cProfile -o result.out -s cumulative env.py

gprof2dot -f pstats result.out | dot -Tpng -o result.png
```



# Usage


### Fast version for training
```python
from pool_env import Env

Env.set_speed(999)
state = Env.get_state()
Env.act(angle=0.0, v_cue=2.0)
Env.plot_table('test1.jpg')
Env.set_state(state)
Env.plot_table('test2.jpg')

```

### slow version for generating gif

```python
from pool_env import Env

Env.set_speed(0.032)   # 1 / 0.0032 = 31.25 fps 
state = Env.get_state()
Env.act(angle=0.0, v_cue=2.0, gif_filename='test.gif')
Env.plot_table('test.jpg')

```
