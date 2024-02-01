FROM python:3.11

WORKDIR /core

COPY ./core /core
COPY ./libs /hant_libs

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install -e /hant_libs/corelib
RUN pip install -e /hant_libs/agentlib
RUN pip install -e /hant_libs/queuelib

CMD ["python", "-m", "core"]