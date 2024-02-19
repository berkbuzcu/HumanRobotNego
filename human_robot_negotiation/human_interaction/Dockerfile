FROM python:3.11

ADD ./human_interaction /human_interaction
ADD ./libs /hant_libs

WORKDIR /human_interaction

RUN pip install -e /hant_libs/queuelib
RUN pip install -e /hant_libs/corelib

RUN pip install -r requirements.txt

RUN python -m nltk.downloader punkt
RUN python -m nltk.downloader averaged_perceptron_tagger

CMD ["python", "-u", "-m", "speech"]