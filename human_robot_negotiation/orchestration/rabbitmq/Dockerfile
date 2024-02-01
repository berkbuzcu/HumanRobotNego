FROM rabbitmq:management
ADD rabbitmq.config /etc/rabbitmq/
ADD definitions.json /etc/rabbitmq/

EXPOSE 5672 15672

RUN chown rabbitmq:rabbitmq /etc/rabbitmq/rabbitmq.config /etc/rabbitmq/definitions.json

CMD ["rabbitmq-server"]