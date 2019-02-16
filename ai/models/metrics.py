"""Define various metrics."""
import tensorflow as tf

# pylint: disable-msg=C0111, C0103


def top2_acc(labels, predictions):
    metr = {}
    metr['top1'] = tf.metrics.mean(
        tf.nn.in_top_k(predictions=predictions, targets=labels, k=1))
    metr['top2'] = tf.metrics.mean(
        tf.nn.in_top_k(predictions=predictions, targets=labels, k=2))
    for k in metr:
        tf.summary.scalar(k, metr[k])
    return metr


def rmse(labels, predictions):
    metr = {}

    metr['value_mse'] = tf.metrics.root_mean_squared_error(
        predictions=predictions[:, 0], labels=labels[:, 0])
    metr['speed_mse'] = tf.metrics.root_mean_squared_error(
        predictions=predictions[:, 1], labels=labels[:, 1])
    for k in metr:
        tf.summary.scalar(k, metr[k])
    return metr


if __name__ == '__main__':
    pass
