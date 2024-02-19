FROM tensorflow/tensorflow:2.12.0-gpu

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

ADD ./libs /hant_libs
ADD ./emotion_analysis/requirements.txt /emotion_analysis/requirements.txt

WORKDIR /hant_libs/queuelib
RUN python3 setup.py install

ADD ./emotion_analysis /emotion_analysis
WORKDIR /emotion_analysis

RUN pip install -r /emotion_analysis/requirements.txt
RUN pip install /hant_libs/queuelib

ENTRYPOINT ["python3", "-m", "emotion_analysis"]
