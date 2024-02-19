FROM python:3.11

ADD ./human_interaction /human_interaction
ADD ./libs /hant_libs

WORKDIR /human_interaction

RUN pip install -e /hant_libs/queuelib

CMD ["python", "-u", "-m", "speech"]