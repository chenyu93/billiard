"""Tools for generate serving model"""

import tensorflow as tf

from services.render import test
# pylint: disable-msg=C0103

state, tensor = test()
t_shape = tensor.shape


def export_input_fn():
    """define serving input funciton"""
    features = {'X': tf.placeholder(tf.float32, [None] + list(t_shape))}

    return tf.estimator.export.build_raw_serving_input_receiver_fn(features)
