# Use an official Python 2.7 image as a parent image
FROM python:2.7

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y libboost-all-dev libqt4-dev libxml2-utils lib32z1 lib32stdc++6

# Download and install pynaoqi
WORKDIR /opt
RUN wget https://community-static.aldebaran.com/resources/2.5.5/sdk-python/pynaoqi-python2.7-2.5.5.5-linux64.tar.gz && \
    tar -xzvf pynaoqi-python2.7-2.5.5.5-linux64.tar.gz && \
    rm pynaoqi-python2.7-2.5.5.5-linux64.tar.gz

ENV PYTHONPATH /opt/pynaoqi-python2.7-2.5.5.5-linux64/lib/python2.7/site-packages

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "pepper"]