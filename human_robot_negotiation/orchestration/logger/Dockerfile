FROM python:3.11


COPY ./libs /hant_libs
COPY ./orchestration/logger /logger

WORKDIR /logger
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install -e /hant_libs/corelib
RUN pip install -e /hant_libs/agentlib
RUN pip install -e /hant_libs/queuelib

CMD ["python", "-u", "-m", "logger"]