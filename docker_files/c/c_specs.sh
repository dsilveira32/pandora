#!/bin/bash

timeout=$1
attempt_id=$2
test_id=$3
contest_id=$4
fsize=$5
compile_flags=$6
linkage_flags=$7
run_arguments=$8
check_leak=$9

echo "timeout=$1
attempt_id=$2
test_id=$3
contest_id=$4
fsize=$5
compile_flags=$6
linkage_flags=$7
run_arguments=$8
check_leak=$9"

set -e
#trap 'catch erro par2 par3' EXIT

catch() {
  echo "== $1 == Erro catched"
	if [ "$1" != "0" ]; then
		if [ "$1" == "124" ]; then #timeout error code
			echo "Error: Timeout!" > /disco/submission_results/$2/$3.test ;
		fi

		if [ "$1" == "153" ]; then #filesize excceded error code
		  echo "Output is too big"
			echo "Error: Output is too big!" > /disco/submission_results/$2/$3.test ;
		fi

		if [ "$1" == "1" ]; then #compilation error code
			echo "Error" > /disco/submission_results/$2/compilation.result
		fi
		chmod -R 0777 /disco/submission_results/$2/
		cp -r /usr/src/compiled/* /disco/tmp/$2/ 2>/dev/null || :
		chmod -R 0777 /disco/tmp/$2/
		exit 0
    #echo "Test error: Unexpected error $1 ocurred"  #> /disco/submission_results/$attempt_id/$test_id.test ; exit 0 #> /disco/submission_results/$attempt_id/$test_id.out ; exit 0
	else
		chmod -R 0777 /disco/submission_results/$2/
		cp -r /usr/src/compiled/* /disco/tmp/$2/ 2>/dev/null || :
		chmod -R 0777 /disco/tmp/$2/
	fi

}

mkdir -p /disco/submission_results/$attempt_id/
cp -r /disco/tmp/$attempt_id/* /usr/src/compiled/ 2>/dev/null || :
cp -r /disco/datafiles/$contest_id/* /usr/src/compiled/ 2>/dev/null  || :
cd /disco/submissions/$attempt_id/
ulimit -f $fsize
trap 'catch $? $attempt_id' EXIT

echo "Running Static analisys"
cppcheck --enable=all --check-config /disco/submissions/$attempt_id/ > /disco/submission_results/$attempt_id/static.out

if [ "$test_id" == "0" ]; then # Run compilation
  echo "Running Compilation"
  echo "gcc $compile_flags *.c -I ./src/*.c  -o /usr/src/compiled/program $linkage_flags 2>/disco/submission_results/$attempt_id/compilation.stdout"
  gcc $compile_flags *.c -I ./src/*.c  -o /usr/src/compiled/program $linkage_flags 2>/disco/submission_results/$attempt_id/compilation.stdout
  echo "Ok" > /disco/submission_results/$attempt_id/compilation.result
else # Run test
  trap 'catch $? $attempt_id $test_id' EXIT
	cd /usr/src/compiled
	echo "Running Test"
	echo "/usr/bin/time --quiet -f %U %K %p %e %M %x -o /disco/submission_results/$attempt_id/$test_id.time timeout $timeout ./program < /disco/tests/$test_id/test.in > /disco/submission_results/$attempt_id/$test_id.out && echo Ok > /disco/submission_results/$attempt_id/$test_id.test"
	/usr/bin/time --quiet -f "%U %K %p %e %M %x" -o /disco/submission_results/$attempt_id/$test_id.time timeout $timeout ./program $run_arguments < /disco/tests/$test_id/test.in | ascii > /disco/submission_results/$attempt_id/$test_id.out && echo "Ok" > /disco/submission_results/$attempt_id/$test_id.test
fi




