#https://docs.docker.com/engine/reference/builder/
#docker build -t pyprofgen-img .
#docker run -d --rm --network host --name pyprofgen-app pyprofgen-img
#docker run -d --rm -P --name pyprofgen-app pyprofgen-img
#docker run -d --rm -p 80:80 -p 1883:1883 -p 9001:9001 --name pyprofgen-app pyprofgen-img
#docker logs pyprofgen-app
#docker container stop pyprofgen-app


FROM python:3

ADD . /
ADD main.py /

RUN pip3 install asyncio
RUN pip3 install paho-mqtt

EXPOSE 80
EXPOSE 1883
EXPOSE 9001


CMD [ "python", "main.py" ]