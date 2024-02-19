FROM node:lts-alpine as builder

ADD ./gui/webserver/frontend /frontend
ADD ./gui/webserver/frontend/package.json /frontend
WORKDIR /frontend
RUN yarn install
RUN yarn run start