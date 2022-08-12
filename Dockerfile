#https://docs.docker.com/engine/reference/builder/
#docker build --rm -t pyprofgen:1.1.0 .
#docker save -o pyprofgen-1-1-0.tar pyprofgen:1.1.0
#docker run -d --rm --network host -e MQTT_BROKER_IP=localhost -e MQTT_BROKER_PORT=1883 -e MQTT_BROKER_KEEPALIVE=60 --name pyprofgen-app pyprofgen:1.0.0
#docker logs pyprofgen-app
#docker container stop pyprofgen-app



FROM python:3-alpine

ADD . /
ADD main.py /

RUN pip3 install asyncio
RUN pip3 install paho-mqtt


#start python with unbuffered output option to see print outputs in docker log
CMD [ "python", "-u", "main.py" ]