# pylint: skip-file

from configure import DISPLAY, CAMERA, TableModel, CamTilt, StartShot, CamRadius
from configure import cue_ball, V_CUE_DECIMAL_PLACE
from configure import pool_ball_1, pool_ball_2, pool_ball_3, pool_ball_4, pool_ball_5, pool_ball_6, pool_ball_7, pool_ball_8, pool_ball_9
import sys
import os
import pi3d
import common
import calculate
import time
import logging
import table
from math import sin, cos, radians
from services.action import ident_pocket
import socket
from global_settings import MODEL_VERSION, ALPHA6

# pylint: disable-msg=C0103

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%d %H:%M:%S')

tableid = int(sys.argv[1])
CamEnable = True
cache = {}


start_shot = StartShot.WAITING

# Create Trajectories
traject_list = [(i * 0.1, i * 0.1, i * 0.1) for i in range(500)]
traject_empty_list = [(i * 0, i * 0, i * 0) for i in range(500)]
tracksh = pi3d.Shader("mat_flat")
track = pi3d.Lines(
    vertices=traject_list, material=(1.0, 0.0, 1.0), z=0, line_width=1)
track.set_shader(tracksh)
frame_to_render = []

# Create key presses (keyboard)
MyKeys = pi3d.Keyboard()


while DISPLAY.loop_running():

    # move camera circularly around cue ball
    if CamEnable:
        CAMERA.reset()
        CAMERA.rotateX(-CamTilt)
        CAMERA.rotateY(0)
        CAMERA.position((0, (cue_ball.r[common.Z_AXIS] * common.DIM_RATIO)
                         + (CamRadius * sin(radians(CamTilt))), 0))

    TableModel.draw()

    # Draw Trajectories
    if start_shot == StartShot.AIMING_READY and len(traject_list) > 0:
        track.draw()
        if len(traject_list) < 500:
            for i in range(500 - len(traject_list)):
                traject_list.append(traject_list[-1])
        elif len(traject_list) >= 500:
            traject_list = traject_list[:500]

        track.buf[0].re_init(traject_list)
    else:
        track.buf[0].re_init(traject_empty_list)

    if start_shot == StartShot.SHOT_READY:
        render_index = len(frame_to_render) - 1
        for ball_obj_traject in calculate.PoolBall.instances_traject:
            for ball_obj in calculate.PoolBall.instances:
                if ball_obj_traject.ball_index == ball_obj.ball_index:
                    previous_r = ball_obj.r
                    ball_obj.r = ball_obj_traject.r_to_render[render_index]
                    # ball_obj.w_roll = ball_obj_traject.w_to_render[render_index]
                    ball_obj.present_state = ball_obj_traject.state_to_render[
                        render_index]
                    ball_obj.heading_angle = ball_obj_traject.heading_angle_to_render[
                        render_index]
                    ball_obj.heading_angle_changed = ball_obj_traject.heading_angle_changed_to_render[
                        render_index]
                    ball_obj.move_rotate_draw(
                        t=1 / frame_to_render[render_index],
                        prev_posit=previous_r)
                    break

        DISPLAY.frames_per_second = frame_to_render[render_index]
        render_index += 1
        if render_index >= len(frame_to_render):
            start_shot = StartShot.WAITING
    else:
        for ball_obj in calculate.PoolBall.instances:
            ball_obj.move_draw()
            ball_obj.shadow.draw()

    k = int(input())

    if k == 102:  # key 'F' for aiming
        start_shot = StartShot.AIMING_INITIATED
    elif k == 103:  # key 'G' for shooting
        if start_shot == StartShot.AIMING_READY:
            start_shot = StartShot.SHOT_READY
            render_index = 0
        else:
            start_shot = StartShot.SHOT_INITIATED

    if start_shot == StartShot.SHOT_INITIATED or start_shot == StartShot.AIMING_INITIATED:

        start_time_predict = 0
        start_time_respond = 0
        start_time_over = time.monotonic()
        traject_list = []
        del frame_to_render[:]
        cue_ball.copy_ball_to_traject()

        CamRotation = 0.0
        v_cue = 5
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
        # cue_ball_traject.respond_event(find_traject=True, check_event=False)
        traject_list.append(
            (cue_ball_traject.r.real[common.X_AXIS] * common.DIM_RATIO,
             cue_ball_traject.r.real[common.Z_AXIS] * common.DIM_RATIO,
             cue_ball_traject.r.real[common.Y_AXIS] * common.DIM_RATIO))

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
                traject_list.append((
                    cue_ball_traject.r.real[common.X_AXIS] * common.DIM_RATIO,
                    cue_ball_traject.r.real[common.Z_AXIS] * common.DIM_RATIO,
                    cue_ball_traject.r.real[common.Y_AXIS] * common.DIM_RATIO))
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
            start_time_respond = start_time_respond + (
                time.monotonic() - tmp_time_respond)

            for ball in calculate.PoolBall.instances_traject:
                ball.state_to_render.append(ball.present_state)
                ball.heading_angle_to_render.append(ball.heading_angle)
                ball.heading_angle_changed_to_render.append(
                    ball.heading_angle_changed)

            traject_list.append(
                (cue_ball_traject.r.real[common.X_AXIS] * common.DIM_RATIO,
                 cue_ball_traject.r.real[common.Z_AXIS] * common.DIM_RATIO,
                 cue_ball_traject.r.real[common.Y_AXIS] * common.DIM_RATIO))
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
                start_time_predict = start_time_predict + (
                    time.monotonic() - tmp_time_predict)

        if start_shot == StartShot.SHOT_INITIATED:
            start_shot = StartShot.SHOT_READY
        elif start_shot == StartShot.AIMING_INITIATED:
            start_shot = StartShot.AIMING_READY
        render_index = 0

        if len(traject_list) <= 1:
            del traject_list[:]
