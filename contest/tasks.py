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

from .models import Classification, Team, TeamMember, Atempt, SafeExecError, Contest
from .utils import *
from .routines import run_test


@shared_task(bind=True)
def run_tests(self, atempt_id, contest_id):
	atempt = Atempt.objects.get(id=atempt_id)
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
	steps = n_tests + 1 + 1 +  1 + 1
	# tests + compile + static_analysis + File handling + cleanup
	progress_recorder.set_progress(0, steps, description="Compiling")

	compile_error, atempt.error_description =  compile(contest, paths)
	atempt.compile_error = not compile_error
	atempt.save()

	if atempt.compile_error:
		return 	# if compilation errors or warnings dont bother with running the tests

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
		progress_recorder.set_progress(3+i, steps, description="Running Test " + str(i+1) + " of " + str(n_tests))
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

		if record.result == 2: #timeout
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
		i = i+1
		

	atempt.grade = (round(pct / 100 * contest.max_classification, 0), 0)[mandatory_failed]
	atempt.save()

	progress_recorder.set_progress(4+n_tests, steps, description="Cleaning Up")

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

