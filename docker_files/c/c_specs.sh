#!/bin/bash

show_help() {
    echo "usage:  $BASH_SOURCE --input1 <input1> --input2 <input2> --input3 <input3>";
    echo "                     --input1 - is input 1 .";
    echo "                     --input2 - is input 2 .";
    echo "                     --input3 - is input 3 .";
}

# set default values
timeout = 1;
attempt_id = 1;
test_id = 0;
contest_id = 1;
fsize = 500;
compile_flags = "-Wall -ansi -Wextra -Wpedantic -Werror";
linkage_flags = "-lc";
run_arguments = "";
check_leak = 0;

# Read command line options
declare -a ARGUMENT_LIST=(
    "timeout"
    "attempt"
    "test"
	"contest"
	"fsize"
	"cflags"
	"lflags"
	"runargs"
	"leak"
)

# read arguments
opts=$(getopt \
    --longoptions "$(printf "%s:," "${ARGUMENT_LIST[@]}")" \
    --name "$(basename "$0")" \
    --options "" \
    -- "$@"
)

eval set --$opts

while true; do
    case "$1" in
    h)
        show_help
        exit 0
        ;;
    --timeout)  
        shift
        timeout=$1
        ;;
    --attempt)  
        shift
        attempt=$1
        ;;
    --test)  
        shift
        test=$1
        ;;
    --contest)  
        shift
        contest=$1
        ;;
    --fsize)  
        shift
        fsize=$1
        ;;
    --cflags)  
        shift
        cflags=$1
        ;;
    --lflags)  
        shift
        lflags=$1
        ;;
    --runargs)  
        shift
        runargs=$1
        ;;
    --leak)  
        shift
        leak=$1
        ;;												
      --)
        shift
        break
        ;;
    esac
    shift
done


echo "timeout = $timeout";
echo "attempt_id = $attempt";
echo "test_id = $test";
echo "contest_id = $contest";
echo "fsize = $fsize";
echo "compile_flags = $cflags";
echo "linkage_flags = $lflags";
echo "run_arguments = $runargs";
echo "check_leak = $leak";

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

mkdir -p /disco/submission_results/$attempt/
cp -r /disco/tmp/$attempt/* /usr/src/compiled/ 2>/dev/null || :
cp -r /disco/datafiles/$contest/* /usr/src/compiled/ 2>/dev/null  || :
cd /disco/submissions/$attempt/
ulimit -f $fsize
trap 'catch $? $attempt_id' EXIT

echo "Running Static analisys"
cppcheck --enable=all --check-config /disco/submissions/$attempt/ > /disco/submission_results/$attempt/static.out

if [ "$test" == "0" ]; then # Run compilation
  echo "Running Compilation"
  echo "gcc $flags *.c -o /usr/src/compiled/program $flags 2>/disco/submission_results/$attempt/compilation.stdout"
  gcc $cflags *.c -o /usr/src/compiled/program $lflags 2>/disco/submission_results/$attempt/compilation.stdout
  echo "Ok" > /disco/submission_results/$attempt/compilation.result
else # Run test
  trap 'catch $? $attempt_id $test_id' EXIT
	cd /usr/src/compiled
	echo "Running Test"
	echo "/usr/bin/time --quiet -f %U %K %p %e %M %x -o /disco/submission_results/$attempt/$test.time timeout $timeout ./program < /disco/tests/$test/test.in > /disco/submission_results/$attempt/$test.out && echo Ok > /disco/submission_results/$attempt/$test.test"
	/usr/bin/time --quiet -f "%U %K %p %e %M %x" -o /disco/submission_results/$attempt/$test.time timeout $timeout ./program $runargs < /disco/tests/$test/test.in | ascii > /disco/submission_results/$attempt/$test.out && echo "Ok" > /disco/submission_results/$attempt/$test.test
fi
