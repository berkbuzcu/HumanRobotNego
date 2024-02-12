FROM ubuntu

EXPOSE 5000
EXPOSE 5001

COPY backend webserver/backend
COPY frontend webserver/frontend

RUN apt-get update
RUN apt-get install -y ca-certificates curl gnupg

RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
ENV NODE_MAJOR=20
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
RUN apt-get install nodejs npm -y

RUN apt-get install python3.11 python3-pip -y

RUN python3.11 -m pip install --no-cache-dir -r /webserver/backend/requirements.txt

WORKDIR /webserver/frontend

RUN npm install
CMD npm run build

WORKDIR /webserver/backend
CMD ["python", "-m", "backend"]