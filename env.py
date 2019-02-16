# pylint: skip-file

import sys
import os
import pi3d
import common
import random
import calculate
import time
import logging
import table
from math import sin, cos, radians
import socket
import utils
import numpy as np

# pylint: disable-msg=C0103


V_CUE_DECIMAL_PLACE = 10
# Initial Game Type


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%d %H:%M:%S')


frame_to_render = []

utils.create_ball()

# utils.reset_position()
cue_ball = utils.find_ball(0)


for step in range(10):
    render_index = len(frame_to_render) - 1
    for ball_obj_traject in calculate.PoolBall.instances_traject:
        ball_obj = next(i for i in calculate.PoolBall.instances if i.ball_index == ball_obj_traject.ball_index)

        previous_r = ball_obj.r
        ball_obj.r = ball_obj_traject.r_to_render[render_index]
        # ball_obj.w_roll = ball_obj_traject.w_to_render[render_index]
        ball_obj.present_state = ball_obj_traject.state_to_render[
            render_index]
        ball_obj.heading_angle = ball_obj_traject.heading_angle_to_render[
            render_index]
        ball_obj.heading_angle_changed = ball_obj_traject.heading_angle_changed_to_render[
            render_index]
    # utils.plot_table(f'test{step}.jpg')

    import time
    time.sleep(1)

    # traject_list = []
    del frame_to_render[:]
    cue_ball.copy_ball_to_traject()

    CamRotation = random.random() * 360
    v_cue = 15
    cue_angle = 0
    top_back_spin = 0
    left_right_spin = 0

    for ball_obj in calculate.PoolBall.instances_traject:
        if ball_obj.ball_index == 0:  # cue_ball's index = 0
            cue_ball_traject = ball_obj

    v, w = calculate.cal_cue_impact(
        a=table.BilliardTable.r * left_right_spin / 100,
        b=table.BilliardTable.r * top_back_spin / 100,
        theta=cue_angle,
        v_cue=v_cue / V_CUE_DECIMAL_PLACE)
    cue_ball_traject.init_collide_outcome(
        state=calculate.STATIONARY_STATE,
        heading_angle=(CamRotation + 360) % 360,
        v=v,
        w=w,
        u=calculate.cal_relative_velo_impact(v, w),
        cue_stick_collide=True)
    cue_ball_traject.update_state_collide()

    calculate.PoolBall.t_table = 0
    time_to_event = cue_ball_traject.find_time_to_collision(
        find_traject=True)
    normal_loop = int(time_to_event / common.NOR_SAMP_PERIOD)
    remainder_time = time_to_event % common.NOR_SAMP_PERIOD
    tstart = time.time()
    while True:
        # No events occurred in normal loop
        for i in range(normal_loop):
            calculate.PoolBall.t_table += common.NOR_SAMP_PERIOD
            for ball in calculate.PoolBall.instances_traject:
                ball.advance_state(common.NOR_SAMP_PERIOD)
                ball.r_to_render.append(ball.r)
                # ball.w_to_render.append(ball.w_roll)
                ball.state_to_render.append(ball.present_state)
                ball.heading_angle_to_render.append(ball.heading_angle)
                ball.heading_angle_changed_to_render.append(False)

            frame_to_render.append(common.NOR_FRAME_PER_SEC)

        # Events occurred in the lasted loop
        calculate.PoolBall.t_table += remainder_time
        for ball in calculate.PoolBall.instances_traject:
            ball.advance_state(remainder_time)
            ball.r_to_render.append(ball.r)
            # ball.w_to_render.append(ball.w_roll)
            ball.heading_angle_changed = False

        tmp_time_respond = time.monotonic()
        cue_ball_traject.respond_event(find_traject=True, check_event=True)


        for ball in calculate.PoolBall.instances_traject:
            ball.state_to_render.append(ball.present_state)
            ball.heading_angle_to_render.append(ball.heading_angle)
            ball.heading_angle_changed_to_render.append(
                ball.heading_angle_changed)

        if remainder_time:
            frame_to_render.append(
                common.NOR_FRAME_PER_SEC
                * (common.NOR_SAMP_PERIOD / remainder_time))
        else:
            frame_to_render.append(common.NOR_FRAME_PER_SEC)

        if all(ball_obj.present_state == calculate.STATIONARY_STATE
               for ball_obj in calculate.PoolBall.instances_traject):
            break
        elif time.time() - tstart > 2:
            print('timeout')
            break
        else:
            tmp_time_predict = time.monotonic()
            time_to_event = cue_ball_traject.find_time_to_collision(
                find_traject=True)
            normal_loop = int(time_to_event / common.NOR_SAMP_PERIOD)
            remainder_time = time_to_event % common.NOR_SAMP_PERIOD

    render_index = 0
