#https://docs.docker.com/engine/reference/builder/
#docker build -t pyprofgen-img .
#docker run -d --rm --network host --name pyprofgen-container pyprofgen-img
#docker run -d --rm -p 1883:1883 --network host --name pyprofgen-container pyprofgen-img
#docker logs pyprofgen-container
#docker container stop pyprofgen-container


FROM python:3

ADD . /
ADD main.py /

RUN pip3 install asyncio
RUN pip3 install paho-mqtt

EXPOSE 1883

CMD [ "python", "main.py" ]