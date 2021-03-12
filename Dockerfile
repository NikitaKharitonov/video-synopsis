FROM python:3.7

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

COPY . /usr/src/app/
RUN pip install -r requirements.txt
RUN python -m pip install https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow_cpu-2.4.0-cp37-cp37m-manylinux2010_x86_64.whl
RUN pip install opencv-python
RUN apt-get update ##[edited]
RUN apt-get install ffmpeg libsm6 libxext6  -y

CMD [ "python", "app.py" ]