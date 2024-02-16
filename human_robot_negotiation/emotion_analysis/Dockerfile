FROM tensorflow/tensorflow:2.12.0-gpu

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR /emotion_analysis

RUN pip3 install -r requirements.txt
RUN pip3 install -e /hant_libs/queuelib
# COPY ./ /emotion_analysis

CMD ["python", "-m", "emotion_analysis"]