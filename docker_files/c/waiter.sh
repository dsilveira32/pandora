#!/bin/bash

wait_file() {
  local file="$1"; shift
  local wait_seconds="${1:-10}"; shift # 10 seconds as default timeout

  until test $((wait_seconds--)) -eq 0 -o -e "$file" ; do sleep 1; done

  ((++wait_seconds))
}

show_help() {
    echo "usage:  $BASH_SOURCE --input1 <input1> --input2 <input2> --input3 <input3>";
    echo "                     --input1 - is input 1 .";
    echo "                     --input2 - is input 2 .";
    echo "                     --input3 - is input 3 .";
}

# Read command line options
declare -a ARGUMENT_LIST=(
    "attempt"
	"timeout"
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
    --attempt)  
        shift
        attempt=$1
        ;;											
    --timeout)  
        shift
        timeout=$1
        ;;
      --)
        shift
        break
        ;;
    esac
    shift
done


echo "attempt_id = $attempt";
echo "timemout = $timeout";

echo "waiting for finish signal"

mkdir -p /disco/submission_results/$attempt/

# Wait at most $timeout seconds for the server.log file to appear
status_file=/disco/submission_results/$attempt/status.info

wait_file "$status_file" $timeout || {
  echo "Tired of waiting... going bananas!"
  exit 1
}