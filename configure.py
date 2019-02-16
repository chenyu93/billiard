# pylint: skip-file

# The MIT License (MIT)
#
# Copyright (c) 2016 Utthawut Bootdee
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals


import time
import pi3d
import common
import table
import calculate
import random
import numpy as np

# pylint: disable-msg=C0103


class StartShot(object):
    WAITING = 0
    AIMING_INITIATED = 1
    AIMING_READY = 2
    SHOT_INITIATED = 3
    SHOT_READY = 4


# Constant/Maximum value
V_CUE_DECIMAL_PLACE = 10
MAX_CAM_ROTATION_R = 360
MAX_CAM_ROTATION_L = -360
MAX_CAM_TILT = 90
MAX_V_CUE = 40

# Load display screen
DISPLAY = pi3d.Display.create(x=120, y=100, w=110 * 5, h=190 * 5)

# Initial Game Type
table.BilliardTable.set_detail_auto(
    table_type=table.TableType.POOL,
    table_size=table.TableSize.EIGHT_FT,
    game_type=table.GameType.POOL_9_BALL)
calculate.BilliardBall.set_r(table.BilliardTable.r)
calculate.BilliardBall.set_mass(common.DEF_BALL_MASS, common.DEF_CUE_MASS)
calculate.CalConst.initial_constant()

# Create Shader
BallShader = pi3d.Shader("mat_reflect")
TableShader = BallShader
ShadowShader = pi3d.Shader("uv_flat")
Normtex = pi3d.Texture("media/textures/grasstile_n.jpg")
Shinetex = pi3d.Texture("media/textures/photosphere_small.jpg")
Shadowtex = pi3d.Texture("media/textures/shadow.png")

# Create Light
light_source = pi3d.Light(
    lightpos=(10,
              -(table.BilliardTable.table_height + calculate.BilliardBall.r) *
              common.DIM_RATIO * 5.2, 1),
    lightcol=(0.9, 0.9, 0.8),
    lightamb=(0.3, 0.3, 0.3),
    is_point=False)

# Create Table
TableModel = pi3d.Model(
    file_string='media/models/Pool_Table_8ft.obj',
    name='Table',
    sx=common.DIM_RATIO,
    sy=common.DIM_RATIO,
    sz=common.DIM_RATIO,
    light=light_source)
TableModel.set_shader(TableShader)
TableModel.set_normal_shine(Normtex, 500.0, Shinetex, 0.05, bump_factor=0.1)


# Create Ball
r_breaking = table.BilliardTable.r
r_epsil_breaking = table.BilliardTable.r_epsil
DIAMETER = r_epsil_breaking + r_epsil_breaking

ref1 = [
    0, table.BilliardTable.bot_rail_r + DIAMETER * 30,
    table.BilliardTable.table_height + table.BilliardTable.r
]

ref2 = [
    ref1[common.X_AXIS] + r_epsil_breaking,
    ref1[common.Y_AXIS] - common.COS_30 * DIAMETER,
    table.BilliardTable.table_height + table.BilliardTable.r
]

ref3 = [
    ref1[common.X_AXIS] + r_epsil_breaking,
    ref1[common.Y_AXIS] + common.COS_30 * DIAMETER,
    table.BilliardTable.table_height + table.BilliardTable.r
]
cue_pos = np.array([
    0, table.BilliardTable.bot_rail_r + DIAMETER * 10,
    table.BilliardTable.table_height + table.BilliardTable.r
])
pos_1 = np.array([
    ref1[common.X_AXIS], ref2[common.Y_AXIS] - common.COS_30 * DIAMETER,
    table.BilliardTable.table_height + table.BilliardTable.r
])

pos_9 = np.array([
    ref1[common.X_AXIS], ref3[common.Y_AXIS] + common.COS_30 * DIAMETER,
    table.BilliardTable.table_height + table.BilliardTable.r
])
pos = [
    np.array([
        0, table.BilliardTable.bot_rail_r + DIAMETER * 30,
        table.BilliardTable.table_height + table.BilliardTable.r
    ]),
    np.array([
        ref1[common.X_AXIS] + DIAMETER, ref1[common.Y_AXIS],
        table.BilliardTable.table_height + table.BilliardTable.r
    ]),
    np.array([
        ref1[common.X_AXIS] - DIAMETER, ref1[common.Y_AXIS],
        table.BilliardTable.table_height + table.BilliardTable.r
    ]),
    np.array([
        ref1[common.X_AXIS] + r_epsil_breaking,
        ref1[common.Y_AXIS] - common.COS_30 * DIAMETER,
        table.BilliardTable.table_height + table.BilliardTable.r
    ]),
    np.array([
        ref1[common.X_AXIS] - r_epsil_breaking,
        ref1[common.Y_AXIS] - common.COS_30 * DIAMETER,
        table.BilliardTable.table_height + table.BilliardTable.r
    ]),
    np.array([
        ref1[common.X_AXIS] + r_epsil_breaking,
        ref1[common.Y_AXIS] + common.COS_30 * DIAMETER,
        table.BilliardTable.table_height + table.BilliardTable.r
    ]),
    np.array([
        ref1[common.X_AXIS] - r_epsil_breaking,
        ref1[common.Y_AXIS] + common.COS_30 * DIAMETER,
        table.BilliardTable.table_height + table.BilliardTable.r
    ])
]
random.shuffle(pos)
pos = [cue_pos, pos_1] + pos + [pos_9]
cue_ball = calculate.PoolBall(
    name="Cue_Ball",
    ball_index=0,
    state=calculate.STATIONARY_STATE,
    r=pos[0],
    v=common.ZERO_VECTOR,
    w=common.ZERO_VECTOR,
    u=common.ZERO_VECTOR,
    heading_angle=0,
    traject_instance=False,
    light=light_source)
pool_ball_5 = calculate.PoolBall(
    name="Pool_Ball_5",
    ball_index=5,
    state=calculate.STATIONARY_STATE,
    r=pos[5],
    v=common.ZERO_VECTOR,
    w=common.ZERO_VECTOR,
    u=common.ZERO_VECTOR,
    heading_angle=0,
    traject_instance=False,
    light=light_source)
pool_ball_6 = calculate.PoolBall(
    name="Pool_Ball_6",
    ball_index=6,
    state=calculate.STATIONARY_STATE,
    r=pos[6],
    v=common.ZERO_VECTOR,
    w=common.ZERO_VECTOR,
    u=common.ZERO_VECTOR,
    heading_angle=0,
    traject_instance=False,
    light=light_source)
pool_ball_4 = calculate.PoolBall(
    name="Pool_Ball_4",
    ball_index=4,
    state=calculate.STATIONARY_STATE,
    r=pos[4],
    v=common.ZERO_VECTOR,
    w=common.ZERO_VECTOR,
    u=common.ZERO_VECTOR,
    heading_angle=0,
    traject_instance=False,
    light=light_source)
pool_ball_3 = calculate.PoolBall(
    name="Pool_Ball_3",
    ball_index=3,
    state=calculate.STATIONARY_STATE,
    r=pos[3],
    v=common.ZERO_VECTOR,
    w=common.ZERO_VECTOR,
    u=common.ZERO_VECTOR,
    heading_angle=0,
    traject_instance=False,
    light=light_source)
pool_ball_2 = calculate.PoolBall(
    name="Pool_Ball_2",
    ball_index=2,
    state=calculate.STATIONARY_STATE,
    r=pos[2],
    v=common.ZERO_VECTOR,
    w=common.ZERO_VECTOR,
    u=common.ZERO_VECTOR,
    heading_angle=0,
    traject_instance=False,
    light=light_source)
pool_ball_1 = calculate.PoolBall(
    name="Pool_Ball_1",
    ball_index=1,
    state=calculate.STATIONARY_STATE,
    r=pos[1],
    v=common.ZERO_VECTOR,
    w=common.ZERO_VECTOR,
    u=common.ZERO_VECTOR,
    heading_angle=0,
    traject_instance=False,
    light=light_source)
pool_ball_8 = calculate.PoolBall(
    name="Pool_Ball_8",
    ball_index=8,
    state=calculate.STATIONARY_STATE,
    r=pos[8],
    v=common.ZERO_VECTOR,
    w=common.ZERO_VECTOR,
    u=common.ZERO_VECTOR,
    heading_angle=0,
    traject_instance=False,
    light=light_source)
pool_ball_7 = calculate.PoolBall(
    name="Pool_Ball_7",
    ball_index=7,
    state=calculate.STATIONARY_STATE,
    r=pos[7],
    v=common.ZERO_VECTOR,
    w=common.ZERO_VECTOR,
    u=common.ZERO_VECTOR,
    heading_angle=0,
    traject_instance=False,
    light=light_source)
pool_ball_9 = calculate.PoolBall(
    name="Pool_Ball_9",
    ball_index=9,
    state=calculate.STATIONARY_STATE,
    r=pos[9],
    v=common.ZERO_VECTOR,
    w=common.ZERO_VECTOR,
    u=common.ZERO_VECTOR,
    heading_angle=0,
    traject_instance=False,
    light=light_source)

for ball_obj in calculate.PoolBall.instances:
    ball_obj.ball_model.set_shader(BallShader)
    ball_obj.ball_model.set_normal_shine(
        Normtex, 0.0, Shinetex, 0.1, is_uv=False, bump_factor=0.0)
    ball_obj.shadow.set_draw_details(ShadowShader, [Shadowtex])

# Initial Input of Cue Stick parameters

v_cue = top_back_spin = left_right_spin = cue_angle = 0


# Initial Frame Render

render_index = 0
# DrawBallFirstTime = True  # Need to fix this
DISPLAY.frames_per_second = common.NOR_FRAME_PER_SEC

# Create Camera
CAMERA = pi3d.Camera.instance()
CamRadius = 30.0  # radius of camera position
CamRotation = 0.0  # rotation of camera
CamTilt = 90.0  # CamTilt of camera
