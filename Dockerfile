FROM debian as builder
LABEL maintainer="Frederic Aoustin <fraoustin@gmail.com>"

RUN apt-get update && apt-get install -y \
        minify \
    && rm -rf /var/lib/apt/lists/* 

RUN mkdir /jlat
RUN mkdir /jlat/files
COPY ./files/ /jlat/files/
WORKDIR /jlat/files/css
RUN minify -o icon.css icon.css
RUN minify -o jlat.css jlat.css
WORKDIR /jlat/files/javascripts
RUN minify -o jlat.js jlat.js

FROM python:3.8-alpine

RUN pip install flask Flask-SQLAlchemy flask-login

RUN mkdir /data
VOLUME /data

RUN mkdir /jlat
COPY . /jlat/
RUN rm -rf /jlat/files
COPY --from=builder /jlat/files /jlat/files
RUN rm -rf /jlat/entrypoint.sh

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN pip install -r /jlat/REQUIREMENTS.txt

ENV JLAT_PORT 5000
ENV JLAT_DEBUG false
ENV JLAT_HOST 0.0.0.0
ENV JLAT_DIR /data

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["jlat"]