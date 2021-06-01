FROM ubuntu:latest
ENV TZ=Europe/Stockholm
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update && apt-get install -y default-jdk wget git && rm -rf /var/lib/apt/lists/*
COPY . /app
RUN wget "http://search.maven.org/remotecontent?filepath=org/python/jython-standalone/2.7.0/jython-standalone-2.7.0.jar" -O app/jython-standalone-2.7.0.jar \
	&& wget https://jitpack.io/com/github/frohoff/ysoserial/master-SNAPSHOT/ysoserial-master-SNAPSHOT.jar -O /app/jars/ysoserial.jar
EXPOSE 8000
WORKDIR /app
ENTRYPOINT ["tail", "-f", "/dev/null"]
