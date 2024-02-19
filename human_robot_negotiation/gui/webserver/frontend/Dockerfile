FROM node:lts-alpine as builder

ADD ./gui/webserver/frontend /frontend
ADD ./gui/webserver/frontend/package.json /frontend
WORKDIR /frontend
RUN yarn install
RUN yarn run build

FROM nginx:1.19.0-alpine
WORKDIR /usr/share/nginx/html
RUN rm -rf ./*
COPY --from=builder /frontend/build .
ENTRYPOINT ["nginx", "-g", "daemon off;"]