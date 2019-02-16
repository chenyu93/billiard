"""Define various train op function."""
import tensorflow as tf
from global_settings import LEARNING_RATE

# pylint: disable-msg=C0111, C0103


class AdamGradClipOptimizer(tf.train.AdamOptimizer):
    def __init__(self,
                 learning_rate=0.001,
                 beta1=0.9,
                 beta2=0.999,
                 epsilon=1e-08,
                 use_locking=False,
                 grad_clip=5.0,
                 name='AdamGradClipOptimizer'):

        super().__init__(
            learning_rate=learning_rate,
            beta1=beta1,
            beta2=beta2,
            epsilon=epsilon,
            use_locking=use_locking,
            name=name,
        )
        self.grad_clip = grad_clip

    def compute_gradients(self, *args, **kwargs):
        gradients = super().compute_gradients(*args, **kwargs)
        return self._clip_gradients(gradients)

    def _clip_gradients(self, gradients):
        for i, (grad, var) in enumerate(gradients):
            if grad is not None:
                gradients[i] = (tf.clip_by_norm(grad, self.grad_clip), var)
        return gradients


def rmsp_decay(loss):
    steps = tf.get_collection(tf.GraphKeys.GLOBAL_STEP)
    if len(steps) == 1:
        step = steps[0]
    else:
        raise Exception('Multiple global steps disallowed')
    rate = tf.train.exponential_decay(LEARNING_RATE, step, 500, 0.97)
    # optimizer = tf.train.AdamOptimizer(rate)
    optimizer = tf.train.RMSPropOptimizer(rate, 0.99, 0.0, 1e-6)
    update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
    with tf.control_dependencies(update_ops):
        train_op = optimizer.minimize(loss, step)
    return train_op


def adam(loss):
    steps = tf.get_collection(tf.GraphKeys.GLOBAL_STEP)
    if len(steps) == 1:
        step = steps[0]
    else:
        raise Exception('Multiple global steps disallowed')
    optimizer = AdamGradClipOptimizer(LEARNING_RATE)
    update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
    with tf.control_dependencies(update_ops):
        train_op = optimizer.minimize(loss, step)
    return train_op
