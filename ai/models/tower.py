import tensorflow as tf
from global_settings import ALPHA4

# pylint: disable-msg=C0111, C0103, W0613


def Q_conv_tower(features, training):
    def conv(kernel_size, strides, filters, padding='SAME'):
        return tf.layers.conv2d(
            x,
            filters=filters,
            kernel_size=(kernel_size, kernel_size),
            strides=(strides, strides),
            padding=padding,
            activation=tf.nn.relu,
            kernel_initializer=conv_initializer,
            kernel_regularizer=regularizer,
            bias_regularizer=regularizer)

    conv_initializer = tf.contrib.layers.xavier_initializer()
    fc_initializer = tf.contrib.layers.xavier_initializer()
    regularizer = tf.contrib.layers.l2_regularizer(ALPHA4)
    x = tf.cast(features['X'], tf.float32)
    for n in [64, 64]:
        x = conv(7, 3, n, 'valid')
        x = tf.layers.batch_normalization(x, scale=False, training=training)

    for n in [128, 128]:
        x = conv(5, 1, n)
        x = tf.layers.batch_normalization(x, scale=False, training=training)

    for n in [256, 256]:
        x = conv(3, 1, n)
        x = tf.layers.batch_normalization(x, scale=False, training=training)

    x = tf.contrib.layers.flatten(x)
    for n in [512]:
        x = tf.layers.dense(
            x,
            n,
            activation=tf.nn.relu,
            kernel_initializer=fc_initializer,
            kernel_regularizer=regularizer,
            bias_regularizer=regularizer)
    x = tf.layers.dense(
        x,
        6,
        activation=None,
        kernel_initializer=fc_initializer,
        kernel_regularizer=regularizer,
        bias_regularizer=regularizer)
    return x


if __name__ == '__main__':
    pass
    #
    # loss = value_loss(logits, label)
    #
    # loss_ = sess.run(
    #     [loss],
    #     feed_dict={
    #         ph: [tensor, tensor, tensor],
    #         label: [[1, 2, 3, 4, 5, 6], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1]]
    #     })
