# pylint: skip-file

import sys
import os
import pi3d
import common
import random
import calculate
import time
import table
from math import sin, cos, radians
import socket
import utils
import numpy as np

# pylint: disable-msg=C0103


utils.create_ball()

# utils.reset_position()
cue_ball = utils.find_ball(0)


class Env:
    frame_to_render = []

    @staticmethod
    def set_speed(speed):
        # 0.032  for 31.25 FPS sample rate; 999 for faster
        common.NOR_SAMP_PERIOD = speed

    @staticmethod
    def plot_animation(filename):
        assert filename.endswith('.gif')
        utils.plot_animation(Env.frame_to_render, filename,
                             common.NOR_SAMP_PERIOD)

    @staticmethod
    def plot_table(filename):
        assert filename.endswith('.jpg') or filename.endswith('.png')
        utils.plot_table(filename)

    @staticmethod
    def get_state():
        positions = np.zeros((10, 3))
        for ball_index in range(10):
            positions[ball_index] = utils.find_ball(ball_index).r
        return positions

    @staticmethod
    def set_state(positions):
        assert positions.shape == (10, 3)
        for ball_index in range(10):
            utils.find_ball(ball_index).r = positions[ball_index]

    @staticmethod
    def act(angle, v_cue, cue_lift=0.0, top_back_spin=0.0, left_right_spin=0.0, gif_filename=None):
        CamRotation = angle
        cue_angle = cue_lift
        assert CamRotation >= 0 and CamRotation < 360
        assert v_cue >= 0 and v_cue < 5.0
        assert cue_angle >= 0 and cue_angle < 60
        assert top_back_spin >= -60 and top_back_spin <= 60
        assert left_right_spin >= -60 and left_right_spin <= 60

        cue_ball.copy_ball_to_traject()
        for ball_obj in calculate.PoolBall.instances_traject:
            if ball_obj.ball_index == 0:  # cue_ball's index = 0
                cue_ball_traject = ball_obj

        v, w = calculate.cal_cue_impact(
            a=table.BilliardTable.r * left_right_spin / 100,
            b=table.BilliardTable.r * top_back_spin / 100,
            theta=cue_angle,
            v_cue=v_cue)
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

                Env.frame_to_render.append(1 / common.NOR_SAMP_PERIOD)

            # Events occurred in the lasted loop
            calculate.PoolBall.t_table += remainder_time
            for ball in calculate.PoolBall.instances_traject:
                ball.advance_state(remainder_time)
                ball.r_to_render.append(ball.r)
                # ball.w_to_render.append(ball.w_roll)
                ball.heading_angle_changed = False

            cue_ball_traject.respond_event(find_traject=True, check_event=True)

            for ball in calculate.PoolBall.instances_traject:
                ball.state_to_render.append(ball.present_state)
                ball.heading_angle_to_render.append(ball.heading_angle)
                ball.heading_angle_changed_to_render.append(
                    ball.heading_angle_changed)

            if remainder_time:
                Env.frame_to_render.append(
                    1 / common.NOR_SAMP_PERIOD
                    * (common.NOR_SAMP_PERIOD / remainder_time))
            else:
                Env.frame_to_render.append(1 / common.NOR_SAMP_PERIOD)

            if all(ball_obj.present_state == calculate.STATIONARY_STATE
                   for ball_obj in calculate.PoolBall.instances_traject):
                break
            else:
                time_to_event = cue_ball_traject.find_time_to_collision(
                    find_traject=True)
                normal_loop = int(time_to_event / common.NOR_SAMP_PERIOD)
                remainder_time = time_to_event % common.NOR_SAMP_PERIOD

        if gif_filename is None:
            utils.move_ball_to_stationary(Env.frame_to_render)
        else:
            Env.plot_animation(gif_filename)
            utils.move_ball_to_stationary(Env.frame_to_render)
        del Env.frame_to_render[:]
