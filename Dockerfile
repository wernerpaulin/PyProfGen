#docker build -t pyprofgen-docker .
#docker run pyprofgen-docker

FROM python:3

ADD . /
ADD main.py /

RUN pip3 install asyncio
RUN pip3 install paho-mqtt

CMD [ "python", "main.py" ]