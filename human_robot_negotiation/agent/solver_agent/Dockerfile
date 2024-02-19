FROM python:3.11

WORKDIR /solver_agent

ADD ./agent/solver_agent /solver_agent
ADD ./libs /hant_libs

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install -e /hant_libs/corelib
RUN pip install -e /hant_libs/agentlib
RUN pip install -e /hant_libs/queuelib

CMD ["python", "-u", "-m", "solver_agent"]