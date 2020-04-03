import datetime
import os
import shutil
import subprocess
import zipfile
from shutil import copyfile
from subprocess import check_output

from django.conf import settings
from django.core.files import File

from .forms import CreateTestModelForm
from .models import Classification, Team, TeamMember, Atempt, SafeExecError
from .utils import *


# check output function
def check_output(command, cwd):
	process = subprocess.Popen(
		command,
		shell=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,
		universal_newlines=True,
		cwd=cwd
	)
	output = process.communicate()
	ret_code = process.poll()
	return output, ret_code


def get_test_contest_details(t_c):
	return t_c.cpu, t_c.mem, t_c.space, t_c.minuid, t_c.maxuid, t_c.core, t_c.nproc, t_c.fsize, t_c.stack, t_c.clock


# ---------------------------------- functions needed in the functions that are needed ---------------------------------
# exec functions
def exec_command(test, contest, submission_dir, obj_file, user_output, user_report, opt_user_file1):
	print_variable_debug("Submission dir: " + str(submission_dir))
	if test.override_exec_options:
		cpu, mem, space, min_uid, max_uid, core, n_proc, f_size, stack, clock = get_test_contest_details(test)
		# cpu = test.cpu
		# mem = test.mem
		# space = test.space
		# minuid = test.minuid
		# maxuid = test.maxuid
		# core = test.core
		# nproc = test.nproc
		# fsize = test.fsize
		# stack = test.stack
		# clock = test.clock
	else:
		cpu, mem, space, min_uid, max_uid, core, n_proc, f_size, stack, clock = get_test_contest_details(contest)
		# cpu = contest.cpu
		# mem = contest.mem
		# space = contest.space
		# minuid = contest.minuid
		# maxuid = contest.maxuid
		# core = contest.core
		# nproc = contest.nproc
		# fsize = contest.fsize
		# stack = contest.stack
		# clock = contest.clock

	exec_cmd = os.path.join(settings.MEDIA_ROOT, "safeexec")
	exec_cmd += " --cpu %d " % cpu
	exec_cmd += "--mem %d " % mem
	exec_cmd += "--space %d " % space
	exec_cmd += "--minuid %d " % min_uid
	exec_cmd += "--maxuid %d " % max_uid
	exec_cmd += "--core %d " % core
	exec_cmd += "--nproc %d " % n_proc
	exec_cmd += "--fsize %d " % f_size
	exec_cmd += "--stack %d " % stack
	exec_cmd += "--clock %d " % clock
	exec_cmd += "--usage %s " % user_report
	exec_cmd += "--exec "

	if test.run_arguments:
		run_args = str(test.run_arguments)
	else:
		run_args = ''

	if opt_user_file1:
		run_args = run_args.replace('%f1%', opt_user_file1)

	ascii_path = os.path.join(settings.MEDIA_ROOT, "ascii")
	# exec_cmd += obj_file + ' ' + run_args + ' < ' + test.input_file.path + ' > ' + user_output
	exec_cmd += obj_file + ' ' + run_args + ' < ' + test.input_file.path + '| ' + ascii_path + ' > ' + user_output

	return exec_cmd


# handle functions
def handle_zip_file(attempt, f, contest):
	print_variable_debug("Handling zip file...")
	src_path = os.path.abspath(f.path)
	src_base = os.path.basename(src_path)
	print_variable_debug(src_base)
	# if '.zip' in src_base:
	submission_dir = os.path.dirname(src_path)

	my_cmd = 'unzip ' + src_path
	print('extraction: ' + my_cmd)
	output, ret = check_output(my_cmd, submission_dir)
	print_variables_debug([
		"Attempt: " + str(attempt),
		"Contest: " + str(contest),
		"Src_base: " + str(src_base),
		"Output: " + str(output),
		"ret: " + str(ret)
	])

	return
	# return True
	# return False


# check in test files
def check_is_in_file(files):
	print_variable_debug("Checking in files")
	variable_debug = []
	for file in files:
		file_parts = file.split('.')
		variable_debug.append(file_parts[0])
		variable_debug.append(file_parts[1])
		file_type = file_parts[len(file_parts) - 1]
		if (not 'in' == file_type)\
			and (not 'inh' == file_type)\
			and (not 'inm' == file_type)\
			and (not 'inmh' == file_type):
			# print_variables_debug(variable_debug)
			print("The file: " + file + " is not an in file!")
			print("Is an " + file_parts[len(file_parts) - 1] + " file type!")
			return False
	print_variables_debug(variable_debug)
	return True


# check out test files
def check_is_out_file(files, n_files):
	if n_files < len(files):
		print("There are more out files than in files!")
		print("There are " + str(len(files)) + " out files and only " + str(n_files) + " in files!")
		return False
	elif n_files > len(files):
		print("There are more in files than out files!")
		print("There are " + str(n_files) + " out files and only " + str(len(files)) + " in files!")
		return False
	else:
		print_variable_debug("Checking out files")
		variable_debug = []
		for file in files:
			file_parts = file.split('.')
			variable_debug.append(file_parts[0])
			variable_debug.append(file_parts[1])
			file_type = file_parts[len(file_parts) - 1]
			if (not 'out' == file_type)\
				and (not 'outh' == file_type)\
				and (not 'outm' == file_type)\
				and (not 'outmh' == file_type):
				variable_debug.append("\nThe file: " + file + " is not an out file!")
				variable_debug.append("\nIs an " + file_parts[len(file_parts) - 1] + " file type!")
				print_variables_debug(variable_debug)
				return False
		print_variables_debug(variable_debug)
		return True


# check if the test files are for the contest
def check_is_for_this_contest_file(files, contest):
	print_variable_debug("Checking if the files are for the selected contest")
	variable_debug = []
	for file in files:
		file_parts = file.split('.')
		variable_debug.append(file_parts[0])
		variable_debug.append(file_parts[1])
		if contest.short_name not in file_parts[0]:
			print_variables_debug(variable_debug)
			print("The file: " + file + " is not for this contest")
			print("This contest short name is: " + str(contest.short_name))
			return False
	# print_variables_debug(variable_debug)
	return True


def deleting_previous_unzips(extract_dir):
	right_dir = False
	path_to_dir_to_remove = ""
	for c in os.walk(str(extract_dir)):
		print_variable_debug("searching " + str(c))
		for file in c[2]:
			file_path = str(c[0]) + "/" + str(file)
			if os.path.exists(file_path):
				os.remove(file_path)
		if right_dir:
			path_to_dir_to_remove = c[0]
		elif c[1] is not []:
			right_dir = True

	if os.path.exists(path_to_dir_to_remove):
		os.rmdir(path_to_dir_to_remove)


# unzip zip file
def unzip_zip_file(zip_path, f, in_out):
	extract_dir = os.path.dirname(zip_path) + '/temp' + str(in_out)
	file_name = str(os.path.basename(zip_path))

	print_variable_debug("Checking for previous unzips")
	deleting_previous_unzips(extract_dir)

	print_variable_debug("Double checking for previous unzips")
	deleting_previous_unzips(extract_dir)

	print_variable_debug("Unzipping file " + str(file_name))
	with zipfile.ZipFile(f, 'r') as in_files:
		print_variable_debug("Extracting file " + str(file_name) + " to " + str(extract_dir))
		count = 0
		in_files.extractall(extract_dir)
	print_variable_debug("File " + str(file_name) + " unzipped")

	return


# -------------------------------------------------- functions needed --------------------------------------------------
# check in files
def check_in_files(f, contest):
	# set the zip path
	zip_path = os.path.abspath(f.path)
	zip_dir = os.path.dirname(zip_path)

	# unzip zip file
	unzip_zip_file(zip_path, f, '/in')

	# find the last branch level
	count = 0
	for c in os.walk(str(zip_dir) + '/temp/in'):
		print_variable_debug("searching " + str(c))
		count += 1

	# for the last branch level
	file_tree_branch = 0
	for files in os.walk(str(zip_dir) + '/temp/in'):
		file_tree_branch += 1
		if file_tree_branch == count:
			# print_variable_debug("Branch founded!")
			# check if the files are for this contest
			if check_is_for_this_contest_file(files[len(files) - 1], contest):
				print_variable_debug("Is for this contest!")
				# check if they are in files
				if check_is_in_file(files[len(files) - 1]):
					print_variable_debug("Are in files!")
					# if the files are correct return them
					return files[2]

	print_variable_debug("Leaving!")

	# if the files have some problem, return an empty list
	return []


# check out files
def check_out_files(f, contest, files_max_length):
	# set the zip path
	zip_path = os.path.abspath(f.path)
	zip_dir = os.path.dirname(zip_path)

	# unzip zip file
	unzip_zip_file(zip_path, f, '/out')

	# check last branch
	count = 0
	for c in os.walk(str(zip_dir) + '/temp/out'):
		print_variable_debug("searching " + str(c))
		count += 1

	# for the last branch
	file_tree_branch = 0
	for files in os.walk(str(zip_dir) + '/temp/out'):
		file_tree_branch += 1
		if file_tree_branch == count:
			# print_variable_debug("Branch founded!")
			# check if the files are for this contest
			if check_is_for_this_contest_file(files[len(files) - 1], contest):
				print_variable_debug("Is for this contest!")
				# check if they are out files
				if check_is_out_file(files[len(files) - 1], files_max_length):
					print_variable_debug("Are out files!")
					# if the files are correct return them
					return files[2]

	print_variable_debug("Leaving!")
	# if the files have some problem, return an empty list
	return []


def create_test(request, in_files, out_files, contest):
	weight = int(len(in_files))
	benchmark = False

	form = CreateTestModelForm(request.POST or None)
	print("Form of the test is: " + str(form.is_valid()))
	if form.is_valid():
		for i in range(len(in_files) - 1):
			obj = form.save(commit=False)
			obj.contest = contest
			obj.weight_pct = weight
			obj.input_file = in_files[i]
			obj.output_file = out_files[i]
			if not benchmark:
				obj.use_for_time_benchmark = False
				obj.use_for_memory_benchmark = False
				obj.mandatory = False
			else:
				obj.use_for_time_benchmark = True
				obj.use_for_memory_benchmark = True
				obj.mandatory = True
				benchmark = False

			obj.save()
	return


def handle_uploaded_file(atempt, f, contest):
	print_variable_debug("Handling zip file...")
	print_variable_debug("\"SafeExecError.objects.all()\"")
	safeexec_errors = SafeExecError.objects.all()
	print_variable_debug(safeexec_errors)

	print_variable_debug("\"SafeExecError.objects.get(description='OK')\"")
	safeexec_ok = SafeExecError.objects.get(description='OK')
	print_variable_debug(safeexec_ok)

	src_path = os.path.abspath(f.path)
	src_base = os.path.basename(src_path)
	print_variable_debug(src_base)
	(src_name, ext) = os.path.splitext(src_base)
	safeexec_timeout = SafeExecError.objects.get(description='Time Limit Exceeded')

	# print('ext: ' + ext)
	if ext == '.zip':
		handle_zip_file(atempt, f, contest)

	print('source path = ' + src_path)

	submition_dir = os.path.dirname(src_path)
	# obj_file = submition_dir + '/' + src_name + '.user.o'
	obj_file = src_name + '.user.o'

	# print('submition dir = ' + submition_dir)

	atempt.compile_error = False
	# my_cmd = 'gcc ' + contest.compile_flags + ' ' + src_base + ' -o ' + obj_file + ' ' + contest.linkage_flags
	my_cmd = 'gcc ' + contest.compile_flags + ' ' + '*.c ' + ' -I ' + './src/*.c ' + ' -o ' + obj_file + ' ' +\
		contest.linkage_flags
	# my_cmd = 'gcc ' + contest.compile_flags + ' ' + submition_dir + '/*.c ' + ' -I ' + submition_dir + '/src/*.c ' +
	# ' -o ' + obj_file + ' ' + contest.linkage_flags

	print('compilation: ' + my_cmd)
	output, ret = check_output(my_cmd, submition_dir)

	if output[0] != '':
		atempt.compile_error = True
		atempt.error_description = output[0]
		print('compile error... terminating...')
		atempt.save()
		return  # if compilation errors or warnings dont bother with running the tests

	chmod_cmd = "chmod a+w " + submition_dir
	output, ret = check_output(chmod_cmd, submition_dir)
	print_variables_debug([output, ret])

	test_set = contest.test_set.all()

	n_tests = test_set.count()
	mandatory_failed = False
	pct = 0
	atempt.time_benchmark = 0
	atempt.memory_benchmark = 0
	atempt.cpu_time = 0
	atempt.elapsed_time = 0

	for test in test_set:
		record = Classification()
		record.attempt = atempt
		record.test = test
		record.passed = True

		test_out_base = os.path.basename(test.output_file.path)
		(test_out_name, ext) = os.path.splitext(test_out_base)
		user_output = os.path.join(submition_dir, test_out_base + '.user')
		user_report = os.path.join(submition_dir, test_out_name + '.report')
# 				user_output = test_out_base + '.user'
# 				user_report = test_out_name + '.report'

		# copy option file to the same path
		if test.opt_file1:
			opt_file_base = os.path.basename(test.opt_file1.path)
			opt_user_file1 = os.path.join(submition_dir, opt_file_base)
			copyfile(test.opt_file1.path, opt_user_file1)
		else:
			opt_user_file1 = ""

		exec_cmd = exec_command(test, contest, submition_dir, obj_file, user_output, user_report, opt_user_file1)

		print('exec cmd is:')
		print(exec_cmd)

		time_started = datetime.datetime.now()  # Save start time.
		check_output(exec_cmd, submition_dir)
		record.execution_time = round((datetime.datetime.now() - time_started).microseconds / 1000, 0)  # Get execution time.

		# save files
		f = open(user_report, "r")
		lines = f.readlines()
		f.close()
		os.remove(user_report)

		# problematic save
		f = open(user_output)
		record.output.save(user_output, File(f))
		f.close()

		# verify safeexec report
		safeexec_error_description = lines[0][:-1]

		se_obj = SafeExecError.objects.get(description='Other')
		for e in safeexec_errors:
			if e.description in safeexec_error_description:
				se_obj = e
				break

		record.error = se_obj
		record.error_description = safeexec_error_description
		print(safeexec_error_description)

		# lines[1] = elapsed time: 2 seconds
		# lines[2] = memory usage: 1424 kbytes
		# lines[3] = cpu usage: 1.000 seconds
		elapsed = lines[1].split(" ")
		memory = lines[2].split(" ")
		cpu = lines[3].split(" ")
		record.memory_usage = int(memory[2])
		record.cpu_time = float(cpu[2])
		record.elapsed_time = int(elapsed[2])

		# if there was a timeout, chances are the files generated are huge
		# for safety reasons it is better to delete them
		if record.error == safeexec_timeout:
			# delete all files
			os.remove(record.output.path)
			record.output = None

		if record.error != safeexec_ok:
			record.passed = False
			record.save()
			continue

		# uses the diff tool
		diff, ret =\
			check_output('diff -B --ignore-all-space ' + user_output + ' ' + test.output_file.path, submition_dir)

		record.passed = diff[0] == ''

		if contest.automatic_weight:
			test.weight_pct = round(100 / n_tests, 2)
			test.save()

		if record.passed:
			pct += test.weight_pct
			atempt.memory_benchmark += record.memory_usage
			atempt.time_benchmark += record.execution_time
			atempt.cpu_time += record.cpu_time
			atempt.elapsed_time += record.elapsed_time

			if test.use_for_memory_benchmark:
				atempt.memory_benchmark = record.memory_usage
		else:
			record.error_description = 'Wrong Answer'

			if test.mandatory:
				mandatory_failed = True
		record.save()
		os.remove(user_output)

	atempt.grade = (round(pct / 100 * contest.max_classification, 0), 0)[mandatory_failed]
	atempt.save()
	os.remove(os.path.join(submition_dir, obj_file))
	cleanup_past_attempts(atempt.team, atempt)


# get functions
def get_team_members(request, contest_id, team_id):
	print_variable_debug("Request: " + str(request))
	qs = TeamMember.objects.filter(team__contest=contest_id).filter(user__teammember__team_id=team_id).first()

	print_variables_debug(['qs:', qs])

	if not qs:
		return Team.objects.none(), TeamMember.objects.none()

	team_obj = qs.team
	members = team_obj.teammember_set.all()

	return team_obj, members


# get functions
def get_user_team(request, contest_id):
	qs = TeamMember.objects.filter(team__contest=contest_id, user=request.user).first()

	# print_variables_debug(['qs:', qs])

	if not qs:
		return Team.objects.none(), TeamMember.objects.none()

	team_obj = qs.team
	members = team_obj.teammember_set.all()

	return team_obj, members


# get the team attempts
def get_team_attempts(team):
	members_ids = team.teammember_set.values_list('user__id', flat=True).distinct()
	if not members_ids:
		return None

	return Atempt.objects.filter(contest=team.contest, user__in=members_ids).order_by('-date')


def get_test_number(file_parts):
	# print_variable_debug("File parts length: " + str(len(file_parts)))

	if len(file_parts) is 2:

		file_name = file_parts[0]
		# print_variable_debug("File name: " + str(file_name))

		file_name_parts = file_name.split('_')
		# print_variable_debug("File name parts: " + str(file_name_parts))

		file_name_parts_length = len(file_name_parts)
		# print_variable_debug("File name parts length: " + str(file_name_parts_length))

		if file_name_parts_length > 3:
			return -1
		elif file_name_parts_length is 2:
			return file_name_parts[2]
		elif file_name_parts_length is 3:
			try:
				int(file_name_parts[2])
				print_variable_debug("File name part[2]: " + str(file_name_parts[2]))
				return file_name_parts[2]
			except ValueError:
				try:
					int(file_name_parts[1])
					print_variable_debug("File name part[1]: " + str(file_name_parts[1]))
					return file_name_parts[1]
				except ValueError:
					aux = ""
					if 'test' in file_name_parts[1]:
						parts = file_name_parts[1].split('test')

						if '' is parts[0]:
							aux = parts[1] + file_name_parts[2]
						else:
							aux = parts[0] + file_name_parts[2]
					if 'e' in aux:
						file_name_parts = aux.split('e')
						parts = file_name_parts[1].split('e')

						if '' is parts[0]:
							aux = parts[1]
						else:
							aux = parts[0]
					if '_' in aux:
						file_name_parts = aux.split('_')
						parts = file_name_parts[1].split('_')

						if '' is parts[0]:
							aux = parts[1]
						else:
							aux = parts[0]
					return aux

	else:
		return -1


# set tests in order
def set_test_in_order(tests):
	print_variable_debug("Start putting tests in order!")
	tests_in_order = []
	last_number = -1

	# print_variables_debug([
	# 	"Tests: " + str(tests),
	# 	"Tests length: " + str(len(tests))
	# ])

	for i in range(len(tests)):
		# print_variable_debug("I: " + str(i))
		for test in tests:
			# print_variable_debug("Test: " + str(test))
			file_parts = test.split('.')
			# print_variable_debug("Test parts: " + str(file_parts))
			test_number = get_test_number(file_parts)
			print_variables_debug([
				"Test number: " + str(test_number),
				"Last number: " + str(last_number),
				"Last number + 1: " + str(last_number + 1)
			])
			if last_number + 1 == int(str(test_number)):
				print_variables_debug([
					"Test number: " + str(test_number),
					"last_number + 1 == test_number: " + str(last_number + 1 == test_number)
				])
				last_number += 1
				tests_in_order.append(test)
			# file_name = file_parts[0]
			# print_variable_debug(["File name: ", file_name])
			# file_name_parts = file_name.split('_')
			# print_variable_debug(["File name parts: ", file_name_parts])
			# for part in file_name_parts:
			# 	print_variable_debug(["Part: ", part])
			# 	if 'test' in part:
			# 		print_variable_debug("Found the test number")
			# 		test_number_aux = part.split('test')
			# 		test_number = test_number_aux[1]
			# 		print_variable_debug(["Test number: ", test_number])
			# 		if 'e' in test_number:
			# 			test_number = test_number.split('e')[1]
			# 		print_variable_debug(test_number)
			# 		if '_' in test_number:
			# 			test_number = test_number.split('_')[1]
			# 		print_variable_debug(test_number)
			# 		# print_variable_debug(test_number)
			#
			# 		# print_variables_debug([
			# 		# 	last_number + 1,
			# 		# 	int(test_number),
			# 		# 	last_number + 1 == int(test_number),
			# 		# 	last_number + 1 == test_number
			# 		# ])
			# 		if last_number + 1 == int(test_number):
			# 			last_number += 1
			# 			tests_in_order.append(test)

	return tests_in_order


def cleanup_past_attempts(team_obj, attempt_obj):
	attempts_qs = Atempt.objects.filter(team=team_obj).exclude(id=attempt_obj.id).order_by('-date')
	for at in attempts_qs:
		results = at.classification_set.all()
		for res in results:
			if res.output and os.path.isfile(res.output.path):
				os.remove(res.output.path)
			res.output = None

		if at.file and os.path.isfile(at.file.path):
			directory = os.path.dirname(at.file.path)
			shutil.rmtree(directory)
		at.file = None
