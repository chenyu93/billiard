"""start training"""
# pylint: disable-msg=C0111, C0103

import queue
import shutil
import threading
import tensorflow as tf

from ai.lib.model_fn import multiclass_model_fn
from ai.lib.export_model import export_input_fn
from ai.models import Q_conv_tower, value_loss, adam, rmse
from ai.train.sample_memory import np_to_queue, equalweights, get_test_input_fn
from global_settings import MODEL_VERSION, MODEL_DIR, SERVABLE_MODEL_DIR, TRAINED_MODEL_DIR, estconfig

if __name__ == '__main__':
    train_queue = queue.Queue(maxsize=1)
    # start train data collection
    train_data_thr = threading.Thread(
        target=np_to_queue, args=('train%d' % MODEL_VERSION, train_queue))
    train_data_thr.start()

    test_input_fn = get_test_input_fn('test%d' % MODEL_VERSION, 40000)
    print('finish get test data')

    # define classifier
    classifier = tf.estimator.Estimator(
        model_fn=multiclass_model_fn(Q_conv_tower, value_loss, adam, rmse),
        model_dir=MODEL_DIR.format(MODEL_VERSION),
        config=estconfig)

    while True:
        for _ in range(2):
            input_fn = train_queue.get()
            classifier.train(input_fn=input_fn)
            del input_fn
        classifier.evaluate(input_fn=test_input_fn)

    # export
    servable_model_path = classifier.export_savedmodel(SERVABLE_MODEL_DIR,
                                                       export_input_fn())
    shutil.move(servable_model_path, TRAINED_MODEL_DIR.format(MODEL_VERSION))
