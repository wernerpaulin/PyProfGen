#docker build -t pyprofgen-docker .

FROM python:3
ADD . /app
ADD . /helper
ADD main.py /

RUN pip3 install asyncio
RUN pip3 install paho-mqtt

CMD [ "python", "./main.py" ]