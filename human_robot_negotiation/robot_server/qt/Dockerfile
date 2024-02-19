FROM python:3.11

ADD ./robot_server/qt /qt
ADD ./libs /hant_libs

WORKDIR /qt

RUN pip install -r requirements.txt

RUN pip install -e /hant_libs/corelib
RUN pip install -e /hant_libs/queuelib


CMD ["python", "-u", "-m", "qt"]