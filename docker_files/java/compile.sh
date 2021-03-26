#!/bin/bash

echo "Running Compilation"
echo "javac *.java -d /usr/src/compiled/ 2>&1 >/dev/null | ascii > /disco/submission_results/$1/compilation.stdout"
javac ./**/*.java -d /usr/src/compiled/ 2>&1 >/dev/null | ascii > /disco/submission_results/$1/compilation.stdout
if [ "${PIPESTATUS[0]}" -ne "0" ]; then
	exit ${PIPESTATUS[0]}
fi
echo "Ok" > /disco/submission_results/$1/compilation.result
exit 0

