#https://docs.docker.com/engine/reference/builder/
#docker build --rm -t pyprofgen:1.0.1 .
#docker save -o pyprofgen-1-0-1.tar pyprofgen:1.0.1
#docker run -d --rm --network host -e MQTT_BROKER_IP=192.168.1.100 -e MQTT_BROKER_PORT=1883 --name pyprofgen-app pyprofgen-img
#docker logs pyprofgen-app
#docker container stop pyprofgen-app



FROM python:3-alpine

ADD . /
ADD main.py /

RUN pip3 install asyncio
RUN pip3 install paho-mqtt


#start python with unbuffered output option to see print outputs in docker log
CMD [ "python", "-u", "main.py" ]