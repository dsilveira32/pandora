FROM openjdk:8
# RUN apt-get update && apt-get install --only-upgrade bash
COPY time /usr/bin/time
COPY ascii /usr/bin/ascii
COPY java_specs.sh /usr/src/java_specs.sh
COPY java_specs.sh /usr/bin/java_specs.sh
COPY c_specs.sh /usr/bin/c_specs.sh
COPY ascii /usr/bin/ascii
COPY compile.sh /usr/bin/compile.sh
COPY run_java_main.sh /usr/bin/run_java_main.sh
COPY run.sh /usr/bin/run.sh
RUN mkdir /usr/src/compiled/