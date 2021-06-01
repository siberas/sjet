FROM ubuntu:latest
ENV TZ=Europe/Stockholm
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update && apt-get install -y jython wget git && rm -rf /var/lib/apt/lists/*
COPY . /app
RUN wget https://jitpack.io/com/github/frohoff/ysoserial/master-SNAPSHOT/ysoserial-master-SNAPSHOT.jar -O /app/jars/ysoserial.jar
EXPOSE 8000
WORKDIR /app
ENTRYPOINT ["jython", "mjet.py"]
