FROM gcc:4.9
COPY time /usr/bin/time
COPY c_specs.sh /usr/src/c_specs.sh
RUN apt-get update -y && apt install cppcheck -y
CMD /usr/src/c_specs.sh ${timeout} ${attempt} ${test} ${fsize} "${compile_flags}" "${linkage_flags}" ${check_leak} "${run_arguments}"
