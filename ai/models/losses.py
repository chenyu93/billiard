import tensorflow as tf
from global_settings import ALPHA3

# pylint: disable-msg=C0111, C0103

#
# def multiclass_loss(logits, labels, weights):
#     loss = tf.losses.compute_weighted_loss(
#         tf.nn.sparse_softmax_cross_entropy_with_logits(
#             labels=labels, logits=logits),
#         weights=weights)
#     tf.summary.scalar('loss', loss)
#     return loss


def value_loss(logits, labels):
    l_value = tf.losses.mean_squared_error(
        labels=labels[:, 0], predictions=logits[:, 0])
    l_angle = tf.losses.mean_squared_error(
        labels=labels[:, 1], predictions=logits[:, 1])
    l_speed = tf.losses.mean_squared_error(
        labels=labels[:, 2], predictions=logits[:, 2])
    l_lift = tf.losses.mean_squared_error(
        labels=labels[:, 3], predictions=logits[:, 3])
    l_topback = tf.losses.mean_squared_error(
        labels=labels[:, 4], predictions=logits[:, 4])
    l_leftright = tf.losses.mean_squared_error(
        labels=labels[:, 5], predictions=logits[:, 5])
    loss = l_value + ALPHA3 * (
        l_angle + l_speed + l_lift + l_topback + l_leftright)
    tf.summary.scalar('total', loss)
    tf.summary.scalar('value', l_value)
    tf.summary.scalar('angle', l_angle)
    tf.summary.scalar('speed', l_speed)
    tf.summary.scalar('lift', l_lift)
    tf.summary.scalar('topback', l_topback)
    tf.summary.scalar('leftright', l_leftright)
    tf.summary.histogram('hist_values', logits[:, 0])
    tf.summary.histogram('hist_angle', logits[:, 1])
    tf.summary.histogram('hist_speed', logits[:, 2])
    tf.summary.histogram('hist_lift', logits[:, 3])
    tf.summary.histogram('hist_topback', logits[:, 4])
    tf.summary.histogram('hist_leftright', logits[:, 5])
    return loss
