billiard


```bash
pip install shapely msgpack_numpy pi3d


cd speed
python setup.py build_ext -i
```



```bash
python -m cProfile -o result.out -s cumulative env.py

gprof2dot -f pstats result.out | dot -Tpng -o result.png
```
