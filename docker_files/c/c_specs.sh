#!/bin/bash

timeout=$1
attempt_id=$2
test_id=$3
fsize=$4
compile_flags=$5
linkage_flags=$6
check_leak=$7
run_arguments=$8

echo "timeout=$1
attempt_id=$2
test_id=$3
fsize=$4
compile_flags=$5
linkage_flags=$6
check_leak=$7
run_arguments=$8"

set -e
#trap 'catch erro par2 par3' EXIT	

catch() {	
	if [ "$1" != "0" ]; then
		if [ "$1" == "124" ]; then #timeout error code
			echo "Error: Timeout!" > /disco/submission_results/$attempt_id/$test_id.test ;
		fi
		
		if [ "$1" == "153" ]; then #filesize excceded error code
			echo "Error: Output is too big!" > /disco/submission_results/$attempt_id/$test_id.test ;
		fi
		
		if [ "$1" == "1" ]; then #compilation error code
			echo "Error" > /disco/submission_results/$attempt_id/compilation.result
		fi
		chmod -R 0777 /disco/submission_results/$attempt_id/ ; exit 0
    #echo "Test error: Unexpected error $1 ocurred"  #> /disco/submission_results/$attempt_id/$test_id.test ; exit 0 #> /disco/submission_results/$attempt_id/$test_id.out ; exit 0
	else
		chmod -R 0777 /disco/submission_results/$attempt_id/
	fi

}

mkdir -p /disco/submission_results/$attempt_id/
ulimit -f $fsize # 5Mb limit
trap 'catch $? $attempt_id' EXIT
cd /disco/submissions/$attempt_id/

echo "Running Static analisys"
cppcheck --enable=all --check-config /disco/submissions/$attempt_id/ > /disco/submission_results/$attempt_id/static.out

echo "Running Compilation"
echo "gcc $compile_flags *.c -I ./src/*.c  -o /usr/src/program $linkage_flags 2>/disco/submission_results/$attempt_id/compilation.stdout"
gcc $compile_flags *.c -I ./src/*.c  -o /usr/src/program $linkage_flags 2>/disco/submission_results/$attempt_id/compilation.stdout
echo "Ok" > /disco/submission_results/$attempt_id/compilation.result

if [ "$test_id" != "0" ]; then #test
	trap 'catch $? $attempt_id $test_id' EXIT
	cd /usr/src/
	echo "Running Test"
	echo "/usr/bin/time --quiet -f %U %K %p %e %M %x -o /disco/submission_results/$attempt_id/$test_id.time timeout $timeout ./program < /disco/tests/$test_id/test.in > /disco/submission_results/$attempt_id/$test_id.out && echo Ok > /disco/submission_results/$attempt_id/$test_id.test"
	/usr/bin/time --quiet -f "%U %K %p %e %M %x" -o /disco/submission_results/$attempt_id/$test_id.time timeout $timeout ./program < /disco/tests/$test_id/test.in > /disco/submission_results/$attempt_id/$test_id.out && echo "Ok" > /disco/submission_results/$attempt_id/$test_id.test
fi
#arr=(`echo ${3}`);
# for test in "${arr[@]}";
		# do
			# trap 'catch $? $attempt_id $test' EXIT
			# /usr/bin/time --quiet -f "%U %K %p %e %M %x" -o  /disco/submission_results/$attempt_id/$test.time timeout $1 ./program < /disco/tests/$test.in > /disco/submission_results/$attempt_id/$test.out && echo "Test $test OK" && echo "Test OK" > /disco/submission_results/$attempt_id/$test.result
		# done


