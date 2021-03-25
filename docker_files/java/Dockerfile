FROM openjdk:8
COPY time /usr/bin/time
COPY ascii /usr/bin/ascii
COPY java_specs.sh /usr/src/java_specs.sh
COPY java_specs.sh /usr/bin/java_specs.sh
COPY ascii /usr/bin/ascii
COPY compile.sh /usr/bin/compile.sh
COPY run.sh /usr/bin/run.sh
RUN mkdir /usr/src/compiled/
RUN apt-get update -y && apt install cppcheck -y