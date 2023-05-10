import os

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "optical-bond-378222-fcc4858a9e3c.json"

from HANT.hant import HANT

hant = HANT()
hant.exec()