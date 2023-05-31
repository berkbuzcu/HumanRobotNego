import os
import pathlib

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "optical-bond-378222-fcc4858a9e3c.json"

PROJECT_DIR = pathlib.Path(__file__)

