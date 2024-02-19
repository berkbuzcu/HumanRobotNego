FROM python:3.11

ADD ./gui/webserver/backend /backend
ADD ./libs /hant_libs

WORKDIR /backend

RUN pip install -r requirements.txt
RUN pip install -e /hant_libs/queuelib

EXPOSE 5000

CMD ["python", "-m", "backend"]