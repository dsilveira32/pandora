#!/bin/bash

show_help() {
    echo "usage:  $BASH_SOURCE --timeout <seconds> --attempt <id> --test <id> --contest <id> --fsize <KiB> --run_arguments <run arguments> --leak <0|1>";
    echo "                     --input1 - is input 1 .";
    echo "                     --input2 - is input 2 .";
    echo "                     --input3 - is input 3 .";
}

# Read command line options
declare -a ARGUMENT_LIST=(
    "timeout"
    "attempt"
    "test"
    "contest"
    "fsize"
    "run_arguments"
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
    --run_arguments)
        shift
        run_arguments=$1
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
echo "run_arguments = $run_arguments";

set -e

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
echo "Currently not available." > /disco/submission_results/$attempt/static.out

if [ "$test" == "0" ]; then # Run compilation
  compile.sh $attempt
else # Run test
  trap 'catch $? $attempt $test' EXIT
  run.sh $attempt $test $timeout $run_arguments
fi
