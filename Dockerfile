FROM centos:7
MAINTAINER Riszky MF "riszky@biznetgio.com"

RUN yum install -y yum-utils epel-release && \
    yum install -y gcc python36 python36-pip python36-devel postgresql-devel openssl-devel wget

ENV TZ Asia/Jakarta
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN yum install -y crontabs && crond start && \
    yum install sudo -y 

RUN mkdir /app
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt && \
    pip3 install gunicorn

COPY . /app
WORKDIR /app

RUN mkdir /app/log

EXPOSE 6969

RUN echo "nobody    ALL=(ALL) NOPASSWD: ALL">> /etc/sudoers
RUN  chown nobody /app -R
USER nobody
ENTRYPOINT ["sh","./setenv.sh"]