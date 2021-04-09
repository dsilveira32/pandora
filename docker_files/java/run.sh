#!/bin/bash

cd /usr/src/compiled
echo "Running Test"
echo "/usr/bin/time --quiet -f \"%U %K %p %e %M %x\" -o /disco/submission_results/$1/$2.time timeout $3 java Main $4 < /disco/tests/$2/test.in | ascii > /disco/submission_results/$1/$2.out"
echo "Ok" > /disco/submission_results/$1/$2.test
/usr/bin/time --quiet -f "%U %K %p %e %M %x" -o /disco/submission_results/$1/$2.time timeout $3 java Main $4 < /disco/tests/$2/test.in | ascii > /disco/submission_results/$1/$2.out
exit ${PIPESTATUS[0]}
