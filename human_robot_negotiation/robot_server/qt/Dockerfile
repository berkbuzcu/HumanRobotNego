FROM python:3.11s

COPY ./robot_server/qt /qt
COPY ./libs /hant_libs

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install -e /hant_libs/corelib
RUN pip install -e /hant_libs/agentlib
RUN pip install -e /hant_libs/queuelib

WORKDIR /qt

CMD ["python", "-u", "-m", "qt"]