import pi3d
import common
from math import sin, cos, radians
import table
import pathlib
import os
import shutil
import random
import calculate
import numpy as np
import imageio
from PIL import Image


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
    return next(i for i in calculate.PoolBall.instances if i.ball_index == index)



def get_random_initial_pos():
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
    return np.array([cue_pos, pos_1] + pos + [pos_9])

def create_ball():

    # Create Ball
    pos = get_random_initial_pos()
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


# def plot_trajectories():
#     track.draw()
#     if len(traject_list) < 500:
#         for i in range(500 - len(traject_list)):
#             traject_list.append(traject_list[-1])
#     elif len(traject_list) >= 500:
#         traject_list = traject_list[:500]
#
#     track.buf[0].re_init(traject_list)


def move_ball_to_stationary(frame_to_render):
    render_index = len(frame_to_render) - 1

    for ball_obj_traject in calculate.PoolBall.instances_traject:
        ball_obj = next(
            i for i in calculate.PoolBall.instances if i.ball_index == ball_obj_traject.ball_index)

        previous_r = ball_obj.r
        ball_obj.r = ball_obj_traject.r_to_render[render_index]
        # ball_obj.w_roll = ball_obj_traject.w_to_render[render_index]
        ball_obj.present_state = ball_obj_traject.state_to_render[
            render_index]
        ball_obj.heading_angle = ball_obj_traject.heading_angle_to_render[
            render_index]
        ball_obj.heading_angle_changed = ball_obj_traject.heading_angle_changed_to_render[
            render_index]


def plot_animation(frame_to_render, file_name, duration):
    try:
        shutil.rmtree('.gif')
    except:
        pass
    pathlib.Path('.gif').mkdir()
    for render_index in range(len(frame_to_render)):
        if frame_to_render[render_index] != 1/ duration:
            continue
        for ball_obj_traject in calculate.PoolBall.instances_traject:
            ball_obj = next(
                i for i in calculate.PoolBall.instances if i.ball_index == ball_obj_traject.ball_index)

            previous_r = ball_obj.r
            ball_obj.r = ball_obj_traject.r_to_render[render_index]
            # ball_obj.w_roll = ball_obj_traject.w_to_render[render_index]
            ball_obj.present_state = ball_obj_traject.state_to_render[
                render_index]
            ball_obj.heading_angle = ball_obj_traject.heading_angle_to_render[
                render_index]
            ball_obj.heading_angle_changed = ball_obj_traject.heading_angle_changed_to_render[
                render_index]

        DISPLAY.clear()
        CAMERA.reset()
        CAMERA.rotateX(-CamTilt)
        CAMERA.rotateY(0)
        cue_ball = find_ball(0)
        CAMERA.position((0, (cue_ball.r[common.Z_AXIS] * common.DIM_RATIO)
                         + (CamRadius * sin(radians(CamTilt))), 0))

        TableModel.draw()
        for ball_obj in calculate.PoolBall.instances:
            ball_obj.move_draw()

        with DISPLAY.lock:
            DISPLAY.sprites_to_load, to_load = set(), DISPLAY.sprites_to_load
            DISPLAY.sprites.extend(to_load)
        DISPLAY._for_each_sprite(lambda s: s.load_opengl(), to_load)

        DISPLAY._tidy()
        img = pi3d.screenshot()
        im = Image.frombuffer(
            'RGB', (DISPLAY.width, DISPLAY.height), img, 'raw', 'RGB', 0, 1)
        im.thumbnail((im.size[0] // 3, im.size[1] // 3), Image.ANTIALIAS)
        im.save(f'.gif/{100000 + render_index}.png')
    if frame_to_render:
        os.system(f'convert .gif/* .tmp.gif')
        os.system(f'convert .tmp.gif -fuzz 10% -layers Optimize {file_name}')
        print(f'generate {file_name}')

def plot_table(file_name=None):
    """show static table."""
    DISPLAY.clear()
    CAMERA.reset()
    CAMERA.rotateX(-CamTilt)
    CAMERA.rotateY(0)
    cue_ball = find_ball(0)
    CAMERA.position((0, (cue_ball.r[common.Z_AXIS] * common.DIM_RATIO)
                     + (CamRadius * sin(radians(CamTilt))), 0))

    TableModel.draw()
    for ball_obj in calculate.PoolBall.instances:
        ball_obj.move_draw()

    with DISPLAY.lock:
        DISPLAY.sprites_to_load, to_load = set(), DISPLAY.sprites_to_load
        DISPLAY.sprites.extend(to_load)
    DISPLAY._for_each_sprite(lambda s: s.load_opengl(), to_load)

    DISPLAY._tidy()
    if file_name is not None:
        pi3d.screenshot(file_name)
