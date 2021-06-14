#!/bin/bash

cd /usr/src/compiled
echo "Running Test"
echo "/usr/bin/time --quiet -f \"%U %K %p %e %M %x\" -o /disco/submission_results/$1/$2.time timeout $3 ./program $4 < /disco/tests/$2/test.in | ascii > /disco/submission_results/$1/$2.out"
echo "Ok" > /disco/submission_results/$1/$2.test



if [ "$5" = "True" ]
then
	/usr/bin/time --quiet -f "%U %K %p %e %M %x" -o /disco/submission_results/$1/$2.time timeout $(($3*4)) /usr/bin/valgrind --error-exitcode=77 --leak-check=full -q ./program $4 < /disco/tests/$2/test.in | ascii > /disco/submission_results/$1/$2.out
	echo "/usr/bin/time --quiet -f \"%U %K %p %e %M %x\" -o /disco/submission_results/$1/$2.time timeout $(($3*4)) /usr/bin/valgrind --error-exitcode=77 --leak-check=full -q ./program $4 < /disco/tests/$2/test.in | ascii > /disco/submission_results/$1/$2.out"
	#status=${PIPESTATUS[0]}
	exitcode=$(grep -Eo '[0-9]+$' /disco/submission_results/$1/$2.time | head -1)
	exit $exitcode
fi
/usr/bin/time --quiet -f "%U %K %p %e %M %x" -o /disco/submission_results/$1/$2.time timeout $3 ./program $4 < /disco/tests/$2/test.in | ascii > /disco/submission_results/$1/$2.out



#status=${PIPESTATUS[0]}
exitcode=$(grep -Eo '[0-9]+$' /disco/submission_results/$1/$2.time | head -1)
exit $exitcode
