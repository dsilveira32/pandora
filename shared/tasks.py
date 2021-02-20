# Celery
from celery import shared_task
# Celery-progress
from celery_progress.backend import ProgressRecorder
# Task imports
import time
import os, time, subprocess, re
from .routines import *
import datetime
import os
import shutil
import subprocess
import zipfile
import re
from shutil import copyfile
from subprocess import check_output
import json
import difflib
from django.conf import settings
from django.core.files import File
import diff_match_patch
from zipfile import ZipFile

from .models import Classification, Team, Attempt, Contest
from .utils import *
from .routines import run_test


@shared_task(bind=True)
def run_tests(self, attempt_id):
    # docker build -t c_spec_test /home/nunes/Desktop/simulation/
    # docker run --rm -i --env to=10 --env tid=0 --env sid=3 -v /home/nunes/Desktop/simulation/:/disco c_spec_test
    data_path = settings.LOCAL_STATIC_CDN_PATH
    progress_recorder = ProgressRecorder(self)
    attempt = Attempt.getByID(attempt_id)
    tests = attempt.getContest().getTests()
    progress_recorder.set_progress(1, tests.count() + 3, "Running compilation")
    print("Init")
    # Run compilation
    run_docker(data_path, "c_spec_test", 10, 0, attempt.id)
    #Checking compilation
    compilation_output = read_file(os.path.join(data_path, 'submission_results', str(attempt.id), 'compilation.result'))
    mandatory_failed = False
    pct = 0
    timeouts = 0
    if "Ok" in compilation_output:
        attempt.compile_error = False
        attempt.save()
        # Run tests
        i = 1
        for test in tests:
            if timeouts < 2:
                progress_recorder.set_progress(i+2, tests.count() + 3, "Running test "+str(i))
                run_docker(data_path, "c_spec_test", 10, test.getID(), attempt.id)
                classification = Classification()
                classification.attempt = attempt
                classification.test = test
                classification.timeout = False
                classification.result = 0
                test_check = read_file(os.path.join(data_path, 'submission_results', str(attempt.id), str(test.getID()) + ".test"))
                if "Ok" in test_check:
                    program_out_file = os.path.join(data_path, 'submission_results', str(attempt.id), str(test.getID()) + ".out")
                    program_out = read_file_lines(program_out_file)
                    ref_out = test.getOutFileContent()
                    is_same, diffs, diff = get_diffs(program_out, ref_out)
                    print(diffs)
                    print(diff)
                    if is_same:
                        pct += test.weight_pct
                        print("Test passed!")
                        classification.passed = True
                        classification.output = program_out_file
                        classification.diff = diff
                    else:
                        if test.mandatory:
                            mandatory_failed = True
                        classification.passed = False
                        classification.output = program_out_file
                        classification.diff = diff
                else:
                    classification.error_description = test_check
                    if 'Timeout' in test_check:
                        classification.timeout = True
                        timeouts += 1
                i += 1
                print('saving')
                classification.save()
                print('saved')
    else:
        compilation_stdout = read_file(
            os.path.join(data_path, 'submission_results', str(attempt.id), 'compilation.stdout'))
        print(compilation_stdout)
        attempt.compile_error = True
        attempt.error_description = compilation_stdout
        attempt.save()
    progress_recorder.set_progress(tests.count() + 2, tests.count() + 3, "Almost there...")
    attempt.grade = (round(pct / 100 * attempt.getContest().max_classification, 0), 0)[mandatory_failed]
    attempt.save()
    """
    atempt = Attempt.objects.get(id=atempt_id)
    contest = Contest.objects.get(id=contest_id)
    f = atempt.file
    paths = extract(f)
    atempt.time_benchmark = 0
    atempt.memory_benchmark = 0
    atempt.cpu_time = 0
    atempt.elapsed_time = 0
    atempt.grade = 0
    progress_recorder = ProgressRecorder(self)

    test_set = contest.test_set.all()
    n_tests = test_set.count()
    steps = n_tests + 1 + 1 + 1 + 1
    # tests + compile + static_analysis + File handling + cleanup
    progress_recorder.set_progress(0, steps, description="Compiling")

    compile_error, atempt.error_description = compile(contest, paths)
    atempt.compile_error = not compile_error
    atempt.save()

    if atempt.compile_error:
        return  # if compilation errors or warnings dont bother with running the tests

    progress_recorder.set_progress(1, steps, description="Static Analysis")
    atempt.static_analysis = static_analysis(paths)

    progress_recorder.set_progress(2, steps, description="File Handling")
    # copy data files to the same path
    data_files = contest.contesttestdatafile_set.all()
    for dfile in data_files:
        data_file_base = os.path.basename(dfile.data_file.path)
        dfile.user_copy = os.path.join(paths['dir'], data_file_base)
        copyfile(dfile.data_file.path, dfile.user_copy)

    mandatory_failed = False
    pct = 0
    timeouts = 0
    i = 0
    for test in test_set:
        progress_recorder.set_progress(3 + i, steps, description="Running Test " + str(i + 1) + " of " + str(n_tests))
        record = Classification()
        record.attempt = atempt
        record.test = test
        run_test(record, paths, data_files, i)
        record.passed = record.result == 0
        if not record.passed and test.mandatory:
            mandatory_failed = True

        if contest.automatic_weight:
            test.weight_pct = round(100 / n_tests, 2)
            test.save()

        if record.result == 2:  # timeout
            timeouts = timeouts + 1
            if timeouts == 2:
                record.result = 4
                record.error_description += "\nYou reached a maximum allows number of Timeouts"
                record.save()
                break

        if record.passed:
            pct += test.weight_pct
            atempt.time_benchmark += record.execution_time
            atempt.memory_benchmark += record.memory_usage
            atempt.cpu_time += record.execution_time
            atempt.elapsed_time += record.execution_time

        record.save()
        i = i + 1

    atempt.grade = (round(pct / 100 * contest.max_classification, 0), 0)[mandatory_failed]
    atempt.save()

    progress_recorder.set_progress(4 + n_tests, steps, description="Cleaning Up")

    # remove object
    if os.path.isfile(os.path.join(paths['dir'], paths['obj'])):
        os.remove(os.path.join(paths['dir'], paths['obj']))

    # remove extracted files (if submition was a zip)
    for f in paths['zip_files']:
        p = os.path.join(paths['dir'], f)
        if os.path.isfile(p):
            os.remove(p)

    # remove data files from user directory
    for dfile in data_files:
        if os.path.isfile(dfile.user_copy):
            os.remove(dfile.user_copy)

    # remove previous atempts files
    cleanup_past_attempts(atempt.team, atempt)
    
    progress_recorder.set_progress(steps, steps, description="All Done")
    """