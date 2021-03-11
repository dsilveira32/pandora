FROM gcc:latest
COPY time /usr/bin/time
COPY ascii /usr/bin/ascii
COPY c_specs.sh /usr/src/c_specs.sh
COPY c_specs.sh /usr/bin/c_specs.sh
COPY ascii /usr/bin/ascii
RUN mkdir /usr/src/compiled/
RUN apt-get update -y && apt install cppcheck -y
#ENTRYPOINT ["sh", "-c", "c_specs.sh ${timeout} ${attempt} ${test} ${contest} ${fsize} ${compile_flags} ${linkage_flags} ${check_leak} ${run_arguments}"]
#CMD c_specs.sh -to=${timeout} -aid=${attempt} ${test} ${contest} ${fsize} ${compile_flags} ${linkage_flags} ${check_leak} ${run_arguments}
CMD /usr/src/c_specs.sh --timeout ${timeout} --attempt ${attempt} --test ${test} --contest ${contest} --fsize ${fsize} --cflags "${compile_flags}" --lflags "${linkage_flags}" --leak ${check_leak} --runargs "${run_arguments}"
#CMD /usr/src/c_specs.sh