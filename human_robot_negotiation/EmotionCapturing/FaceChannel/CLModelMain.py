'''
Onur Things

import os

os.add_dll_directory("C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.0/bin")
os.add_dll_directory("C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.0/libnvvp")
'''

import tensorflow as tf

gpus = tf.config.list_physical_devices("GPU")
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

from CLModel.cl_model_c3_main_faster import get_arousal_valence
import os
import SessionManager
import time
from timeit import default_timer as timer
from datetime import timedelta


LOG_DIR = "sessions/"
EXPERIMENT_ID = 1
CAMERA_SECS = 2

if __name__ == "__main__":
    experiment = SessionManager.Experiment(EXPERIMENT_ID)

    experiment.start()

    time.sleep(CAMERA_SECS)

    experiment.get_session().close_camera()

    start = timer()
    print(get_arousal_valence(experiment.get_session().log_dir))
    end = timer()

    print("Elapsed Time:", timedelta(seconds=end-start))
