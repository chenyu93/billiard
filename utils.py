import pi3d
import common
from math import sin, cos, radians
import table
import random
import calculate
import numpy as np


table.BilliardTable.set_detail_auto(
    table_type=table.TableType.POOL,
    table_size=table.TableSize.EIGHT_FT,
    game_type=table.GameType.POOL_9_BALL)
calculate.BilliardBall.set_r(table.BilliardTable.r)
calculate.BilliardBall.set_mass(common.DEF_BALL_MASS, common.DEF_CUE_MASS)
calculate.CalConst.initial_constant()

DISPLAY = pi3d.Display.create(x=120, y=100, w=110 * 5, h=190 * 5)
DISPLAY.frames_per_second = 30
BallShader = pi3d.Shader("mat_reflect")
TableShader = BallShader
ShadowShader = pi3d.Shader("uv_flat")
Normtex = pi3d.Texture("media/textures/grasstile_n.jpg")
Shinetex = pi3d.Texture("media/textures/photosphere_small.jpg")
Shadowtex = pi3d.Texture("media/textures/shadow.png")

light_source = pi3d.Light(
    lightpos=(10, -(0.762 + 0.028575) * 10 * 5.2, 1),
    lightcol=(0.9, 0.9, 0.8),
    lightamb=(0.3, 0.3, 0.3),
    is_point=False)

TableModel = pi3d.Model(
    file_string='media/models/Pool_Table_8ft.obj',
    name='Table',
    sx=common.DIM_RATIO,
    sy=common.DIM_RATIO,
    sz=common.DIM_RATIO,
    light=light_source)
TableModel.set_shader(TableShader)
TableModel.set_normal_shine(Normtex, 500.0, Shinetex, 0.05, bump_factor=0.1)

CAMERA = pi3d.Camera.instance()
CamRadius = 30.0  # radius of camera position
CamRotation = 0.0  # rotation of camera
CamTilt = 90.0  # CamTilt of camera

def find_ball(index):
    return next(i for i in calculate.PoolBall.instances if i.ball_index ==index)

def create_ball():

    for i in range(10):
        calculate.PoolBall(name='Cue_Ball' if i == 0 else f'Pool_Ball_{i}',
                           ball_index=i,
                           state=calculate.STATIONARY_STATE,
                           r=[0,0,0],
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


def reset_position():
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
    for i in range(10):
        find_ball(i).r = pos[i]

def plot_trajectories():
    track.draw()
    if len(traject_list) < 500:
        for i in range(500 - len(traject_list)):
            traject_list.append(traject_list[-1])
    elif len(traject_list) >= 500:
        traject_list = traject_list[:500]

    track.buf[0].re_init(traject_list)

def plot_table(file_name):
    DISPLAY.clear()
    CAMERA.reset()
    CAMERA.rotateX(-CamTilt)
    CAMERA.rotateY(0)
    cue_ball = find_ball(0)
    CAMERA.position((0, (cue_ball.r[common.Z_AXIS] * common.DIM_RATIO)
                     + (CamRadius * sin(radians(CamTilt))), 0))

    TableModel.draw()
    for ball_obj in calculate.PoolBall.instances:
        print(ball_obj.ball_index, ball_obj.r)
        ball_obj.move_draw()

    with DISPLAY.lock:
        DISPLAY.sprites_to_load, to_load = set(), DISPLAY.sprites_to_load
        DISPLAY.sprites.extend(to_load)
    DISPLAY._for_each_sprite(lambda s: s.load_opengl(), to_load)

    DISPLAY._tidy()
    pi3d.screenshot(file_name)
