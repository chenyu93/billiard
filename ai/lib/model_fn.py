import tensorflow as tf


def multiclass_model_fn(get_conv, get_loss, get_trainop, get_accuracy):
    def model_fn(features, labels, mode, config):
        logits = get_conv(features, mode == tf.estimator.ModeKeys.TRAIN)
        predictions = tf.argmax(logits, axis=-1)
        export_outputs = {
            'forecast': tf.estimator.export.PredictOutput({
                'probs': logits
            })
        }
        if mode == tf.estimator.ModeKeys.TRAIN:
            loss = get_loss(logits, labels)
            trainop = get_trainop(loss)
            return tf.estimator.EstimatorSpec(
                mode=mode,
                loss=loss,
                train_op=trainop,
                export_outputs=export_outputs)
        elif mode == tf.estimator.ModeKeys.EVAL:
            loss = get_loss(logits, labels)
            eval_metric_ops = get_accuracy(labels, logits)
            return tf.estimator.EstimatorSpec(
                mode=mode,
                loss=loss,
                eval_metric_ops=eval_metric_ops,
                export_outputs=export_outputs)
        elif mode == tf.estimator.ModeKeys.PREDICT:
            return tf.estimator.EstimatorSpec(
                mode=mode,
                predictions=predictions,
                export_outputs=export_outputs)

    return model_fn


def reg_model_fn(get_conv, get_loss, get_trainop, get_accuracy):
    def model_fn(features, labels, mode, config):
        logits = get_conv(features, mode == tf.estimator.ModeKeys.TRAIN)
        export_outputs = {
            'forecast': tf.estimator.export.PredictOutput({
                'value': logits
            })
        }
        if mode == tf.estimator.ModeKeys.TRAIN:
            loss = get_loss(logits, labels)
            trainop = get_trainop(loss)
            return tf.estimator.EstimatorSpec(
                mode=mode,
                loss=loss,
                train_op=trainop,
                export_outputs=export_outputs)
        elif mode == tf.estimator.ModeKeys.EVAL:
            loss = get_loss(logits, labels)
            eval_metric_ops = get_accuracy(labels, logits)
            return tf.estimator.EstimatorSpec(
                mode=mode,
                loss=loss,
                eval_metric_ops=eval_metric_ops,
                export_outputs=export_outputs)
        elif mode == tf.estimator.ModeKeys.PREDICT:
            return tf.estimator.EstimatorSpec(
                mode=mode, predictions=logits, export_outputs=export_outputs)

    return model_fn
