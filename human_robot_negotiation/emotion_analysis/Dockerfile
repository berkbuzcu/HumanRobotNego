# Ref https://docs.rapids.ai/install
#FROM nvcr.io/nvidia/rapidsai/rapidsai:23.06-cuda11.8-runtime-ubuntu22.04-py3.10
FROM tensorflow/tensorflow:latest-gpu

#USER root
#
#ENV LANG en_US.UTF-8
#ENV LC_CTYPE en_US.UTF-8

ADD ./emotion_analysis/requirements.txt /
RUN pip3 install -r /requirements.txt

# RUN apt-get update
#
# RUN apt install -y software-properties-common
# RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin && \
# mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600 && \
# apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub && \
# add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /" && \
# apt-get update && \
# apt-get install -y libcudnn8 && \
# apt-get install -y libcudnn8-dev && \
# apt-get install -y kmod && \
# apt-get install -y nvidia-cuda-toolkit
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# download cudnn https://docs.nvidia.com/deeplearning/cudnn/install-guide/index.html?ncid=em-prod-337416

# COPY ./emotion_analysis/cudnn-local-repo-ubuntu2204-8.9.7.29_1.0-1_amd64.deb /var

WORKDIR /emotion_analysis

# COPY ./ /emotion_analysis

CMD ["python", "-m", "emotion_analysis"]