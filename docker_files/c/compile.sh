#!/bin/bash

echo "Running Compilation"
echo "gcc -Wall -ansi -Wpedantic -Wextra -Werror *.c -o /usr/src/compiled/program  2>/disco/submission_results/$1/compilation.stdout"
gcc $2 *.c $3 -o /usr/src/compiled/program 2>&1 >/dev/null | ascii > /disco/submission_results/$1/compilation.stdout
if [ "${PIPESTATUS[0]}" -ne "0" ]; then
	exit ${PIPESTATUS[0]}
fi
echo "Ok" > /disco/submission_results/$1/compilation.result
exit 0

