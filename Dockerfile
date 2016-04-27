FROM localhost:5000/backend-comm-postgres
MAINTAINER Pål Karlsrud <paal@128.no>

ENV BASE_DIR "/var/index-service"

RUN git clone https://github.com/microserv/index-service ${BASE_DIR}
RUN apk add --update curl postgresql-dev

RUN cp ${BASE_DIR}/indexer.ini /etc/supervisor.d/

WORKDIR ${BASE_DIR}

RUN virtualenv ${BASE_DIR}/venv
ENV PATH ${BASE_DIR}/venv/bin:$PATH

RUN pip install -r requirements.txt
RUN rm -rf /run && mkdir -p /run

EXPOSE 80
