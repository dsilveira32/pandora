import os
import zipfile

from django.core.files import File
from django.shortcuts import render, redirect, get_object_or_404

from contest.forms import CreateTestModelForm, TestForm
from contest.models import Contest, Test
from contest.utils import *
from contest.views.admin_views import superuser_only


# ------------------------------------------------------ routines ------------------------------------------------------
# create test
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


def get_zip_file_path(zip_file):
	zip_path = os.path.abspath(zip_file.path)
	return str(os.path.dirname(zip_path)) + "/temp"


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


# check in files
def check_in_files(zip_path, f, contest):
	# set the zip path
	zip_dir = os.path.dirname(zip_path)

	# unzip zip file
	# unzip_zip_file(zip_path, f, '/in')
	get_tests_from_zip(zip_path, f)
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
def check_out_files(zip_path, contest, files_max_length):
	# set the zip path
	# zip_path = os.path.abspath(f.path)
	zip_dir = os.path.dirname(zip_path)

	# unzip zip file
	# unzip_zip_file(zip_path, f, '/out')

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


def get_test_number(file_parts, short_name):
	# print_variable_debug("File parts length: " + str(len(file_parts)))

	short_name = short_name.lower()

	file_parts_aux = file_parts

	for i in range(len(file_parts_aux)):
		file_parts[i] = file_parts_aux[i].lower()

	if len(file_parts) is 2:

		file_name = file_parts[0]

		file_name_parts = file_name.split('_')

		file_name_parts_length = len(file_name_parts)

		if file_name_parts_length > 3:
			return -1
		elif file_name_parts_length is 1:
			parts = file_name_parts[0].split(short_name)
			try:
				int(parts[0])
				return parts[0]
			except ValueError:
				try:
					int(parts[1])
					return parts[1]
				except ValueError:
					if '' is parts[0]:
						aux = str(parts[1])
					else:
						aux = str(parts[0])
					if 'test' in aux:
						parts = aux.split('test')

						if '' is parts[0]:
							aux = parts[1]
						else:
							aux = parts[0]
					if 'e' in aux:
						parts = aux.split('e')

						if '' is parts[0]:
							aux = parts[1]
						else:
							aux = parts[0]
					return aux

		elif file_name_parts_length is 2:
			try:
				int(file_name_parts[0])
				return file_name_parts[0]
			except ValueError:
				try:
					int(file_name_parts[1])
					return file_name_parts[1]
				except ValueError:
					parts = []
					if short_name in file_name_parts[1]:
						parts = file_name_parts[1].split(short_name)
						if str(parts[0]) is str(parts[1]) is '':
							aux = ""
							if 'test' in file_name_parts[0]:
								parts = file_name_parts[0].split('test')
								if '' is parts[0]:
									aux = str(parts[1])
								else:
									aux = parts[0]
							if 'e' in aux:
								parts = aux.split('e')

								if '' is parts[0]:
									aux = parts[1]
								else:
									aux = parts[0]
							return aux
						elif str(parts[0]) is not '':
							return parts[0]
						elif str(parts[1]) is not '':
							return parts[1]
					elif short_name in file_name_parts[0]:
						parts = file_name_parts[0].split(short_name)
						if str(parts[0]) is str(parts[1]) is '':
							aux = ""
							if 'test' in file_name_parts[1]:
								parts = file_name_parts[1].split('test')
								if '' is parts[0]:
									aux = str(parts[1])
								else:
									aux = parts[0]
							if 'e' in aux:
								parts = aux.split('e')
								if '' is parts[0]:
									aux = parts[1]
								else:
									aux = parts[0]
							return aux
						elif str(parts[0]) is not '':
							return parts[0]
						elif str(parts[1]) is not '':
							return parts[1]
		elif file_name_parts_length is 3:
			try:
				int(file_name_parts[0])
				return file_name_parts[0]
			except ValueError:
				try:
					int(file_name_parts[1])
					return file_name_parts[1]
				except ValueError:
					try:
						int(file_name_parts[2])
						return file_name_parts[2]
					except ValueError:
						return -1

	else:
		return -1


# set tests in order
def set_test_in_order(tests, short_name):
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
			test_number = get_test_number(file_parts, short_name)
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


# ------------------------------------------------ super user functions ------------------------------------------------
@superuser_only
def admin_choose_test(request, id):
	template_name = 'contest/test_chooser.html'

	contest_obj = get_object_or_404(Contest, id=id)
	context = {'contest': contest_obj}
	contest_tests = Test.objects.filter(contest_id=id)
	print_variables_debug(["Test:", contest_tests])
	context.update({'tests': contest_tests})

	form = TestForm(request.POST or None)

	print_form_info_debug(form)

	if form.is_valid():
		t_id = form.cleaned_data.get("test_id")
		# if request.method == 'POST':
		# 	fruits = request.POST.getlist('mandatory')
		# print_variables_debug([form.mandatory])
		if "Edit" not in t_id:
			print_variables_debug(["t_id:", t_id])
			# verificar codigo team join e team status
			return redirect(os.path.join(contest_obj.get_absolute_url(), 'admin-view/test/' + str(t_id) + '/editor/'))
		else:
			# id mandatory weight_pct use_for_time_benchmark use_for_memory_benchmark type_of_feedback
			test_changes = str(t_id).split(" ")
			test_id = test_changes[1]

			print_variables_debug(['\n\nmandatory value:\n\n', request.POST.getlist('mandatory' + test_id),
								   '\n\nweight value:\n\n', request.POST.getlist('weight'),
								   '\n\ntime_benchmark value:\n\n', request.POST.getlist('time_benchmark' + test_id),
								   '\n\nmemory_benchmark value:\n\n', request.POST.getlist('memory_benchmark' + test_id),
								   '\n\nfeedback value:\n\n', request.POST.getlist('feedback')])

			if 'on' in request.POST.getlist('weight' + test_id):
				test_mandatory = True
			else:
				test_mandatory = False
			test_weight = request.POST.getlist('weight')[int(test_id)]
			if 'on' in request.POST.getlist('time_benchmark' + test_id):
				test_time_benchmark = True
			else:
				test_time_benchmark = False
			if 'on' in request.POST.getlist('memory_benchmark' + test_id):
				test_memory_benchmark = True
			else:
				test_memory_benchmark = False
			test_feedback = request.POST.getlist('feedback')[int(test_id) - 1]

			print_variables_debug(["Input\n", test_mandatory, test_weight, test_time_benchmark, test_memory_benchmark,
								   test_feedback])

			test = Test.objects.get(contest_id=id, id=test_id)

			print_variables_debug(["Before\n", test.mandatory, test.weight_pct, test.use_for_time_benchmark,
								   test.use_for_memory_benchmark, test.type_of_feedback])

			test.mandatory = test_mandatory
			test.weight_pct = test_weight
			test.use_for_time_benchmark = test_time_benchmark
			test.use_for_memory_benchmark = test_memory_benchmark
			test.type_of_feedback = test_feedback
			test.save()

			print_variables_debug(["After\n", test.mandatory, test.weight_pct, test.use_for_time_benchmark,
								   test.use_for_memory_benchmark, test.type_of_feedback])

		# print_variables_debug(["test id:", test_id])

	return render(request, template_name, context)


def get_tests_from_zip(zip_path, f):
	extract_dir_temp = str(os.path.dirname(zip_path)) + '/temp/temp'
	extract_dir_in = str(os.path.dirname(zip_path)) + '/temp/in'
	extract_dir_out = str(os.path.dirname(zip_path)) + '/temp/out'

	file_name = str(os.path.basename(zip_path))

	print_variable_debug("Checking for previous unzips")
	deleting_previous_unzips(extract_dir_temp)
	deleting_previous_unzips(extract_dir_in)
	deleting_previous_unzips(extract_dir_out)

	print_variable_debug("Double checking for previous unzips")
	deleting_previous_unzips(extract_dir_temp)
	deleting_previous_unzips(extract_dir_in)
	deleting_previous_unzips(extract_dir_out)

	print_variable_debug("Unzipping file " + str(file_name))
	with zipfile.ZipFile(f, 'r') as in_files:
		print_variable_debug("Extracting file " + str(file_name) + " to " + str(extract_dir_temp))
		in_files.extractall(extract_dir_temp)
	print_variable_debug("File " + str(file_name) + " unzipped")

	if not os.path.isdir(extract_dir_in):
		os.mkdir(extract_dir_in)

	if not os.path.isdir(extract_dir_out):
		os.mkdir(extract_dir_out)

	# count = 0
	#
	# for c in os.walk(os.path.dirname(extract_dir_temp)):
	# 	print(c)
	# 	count += 1

	# pos = 0

	print("start")

	for file in os.walk(os.path.dirname(extract_dir_temp)):
		print("searching in " + str(file))
		# pos += 1
		file_path = file[0]
		file_path_parts = str(file_path).split("/")
		file_dirs = file[1]
		file_files = file[2]
		# print_variables_debug([file_path, file_dirs, file_files])
		# print_variable_debug("\n")
		# print_variable_debug("\n")
		# print_variables_debug(
		# 	[
		# 		"file_dirs == []: " + str(file_dirs == []),
		# 		"str(file_path_parts[len(file_path_parts) - 1]) == \"temp\": " + str(
		# 			str(file_path_parts[len(file_path_parts) - 1]) == "temp"
		# 		),
		# 		str(file_path_parts[len(file_path_parts) - 1])
		# 	]
		# )
		if file_dirs == [] and str(file_path_parts[len(file_path_parts) - 1]) == "temp":  # pos == count:
			# print(str(file_files) + "\n\n")
			for f in file_files:
				# print(f)
				f_parts = f.split('.')
				print(f_parts[len(f_parts) - 1])

				if str(f_parts[len(f_parts) - 1]) == "in":
					os.replace(str(extract_dir_temp) + "/" + str(f), str(extract_dir_in) + "/" + str(f))

				elif str(f_parts[len(f_parts) - 1]) == "out":
					os.replace(str(extract_dir_temp) + "/" + str(f), str(extract_dir_out) + "/" + str(f))

	return


def get_test_in_and_out(zip_in, zip_out, contest):
	short_name = contest.short_name

	in_files = set_test_in_order(
		check_in_files(
			zip_in,
			contest
		),
		short_name
	)
	print_variable_debug(in_files)

	print_variable_debug(zip_in)
	n_tests = len(in_files)
	print_variable_debug(n_tests)

	print_variable_debug(zip_out)

	out_files = set_test_in_order(
		check_out_files(
			zip_out,
			contest,
			len(in_files)
		),
		short_name
	)

	print_variable_debug(out_files)

	return in_files, out_files, n_tests


@superuser_only
def admin_test_creation(request):
	template_name = 'contest/test_creation.html'

	test_form = CreateTestModelForm(request.POST or None, request.FILES or None)
	print_form_info_debug(test_form)
	# test_form = CreateTestModelForm(request.POST or None)
	# print("-----------------------------------The form for the test is: " + str(test_form) +
	#       "-----------------------------------")
	# print("-----------------------------------The form for the test is valid: " + str(test_form.is_valid()) +
	#       "-----------------------------------")
	if test_form.is_valid():
		obj = test_form.save(commit=False)
		contest = obj.contest
		zip_in = obj.input_file
		# zip_out = obj.output_file
		# start debug
		print_variable_debug(obj.contest.short_name)
		print_variable_debug(contest)
		a_ok = True
		# end debug
		if '.zip' in str(zip_in):  # and '.zip' in str(zip_out):
			print_variable_debug(
				"The files: \n" + str(zip_in).split('.')[0] + "\n" + "\nare zip files!"
				# str(zip_out).split('.')[0] + "\nare zip files!"
			)
			# in_files, out_files, n_tests = get_test_in_and_out(
			# 	zip_in,
			# 	zip_out,
			# 	contest
			# )
			zip_path = os.path.abspath(zip_in.path)
			in_files = set_test_in_order(check_in_files(zip_path, zip_in, contest), contest.short_name)
			print_variable_debug(in_files)

			print_variable_debug(zip_in)
			n_tests = len(in_files)
			print_variable_debug(n_tests)

			# print_variable_debug(zip_out)
			out_files = set_test_in_order(check_out_files(zip_path, contest, n_tests), contest.short_name)
			print_variable_debug(out_files)

			print_variable_debug("In files: ")
			print_variables_debug(in_files)
			print_variable_debug("Out files: ")
			print_variables_debug(out_files)

			if len(in_files) > 0 and len(out_files) > 0:

				for i in range(len(in_files)):
					if not in_files[i].split('.')[0] == out_files[i].split('.')[0]:
						a_ok = False
					# print_variables_debug([in_files[i].split('.')[0], out_files[i].split('.')[0], a_ok])

			else:

				a_ok = False

			if a_ok:
				print_variable_debug("There is an out for each in!")
				weight = 100 / n_tests
				benchmark = True
				test_number = 0

				for i in range(n_tests):
					test_number += 1
					form = CreateTestModelForm(request.POST or None, request.FILES or None)
					# test = form.save(commit=False)
					test = Test()
					test.contest = contest
					test.weight_pct = weight
					path = get_zip_file_path(zip_in) + "/in/" + str(in_files[i])
					f = open(path)
					test.input_file.save(in_files[i], File(f))
					f.close()
					path = get_zip_file_path(zip_in) + "/out/" + str(out_files[i])
					f = open(path)
					test.output_file.save(out_files[i], File(f))
					f.close()
					if in_files[i].split('.')[1] == "in":
						test.use_for_time_benchmark = False
						test.use_for_memory_benchmark = False
						test.mandatory = False
						test.type_of_feedback = 1
					elif in_files[i].split('.')[1] == "inh":
						test.use_for_time_benchmark = False
						test.use_for_memory_benchmark = False
						test.mandatory = False
						test.type_of_feedback = 2
					elif in_files[i].split('.')[1] == "inm":

						if not benchmark:
							test.use_for_time_benchmark = False
							test.use_for_memory_benchmark = False
							test.mandatory = True
						else:
							test.use_for_time_benchmark = True
							test.use_for_memory_benchmark = True
							test.mandatory = True
							benchmark = False

						test.type_of_feedback = 1
					elif in_files[i].split('.')[1] == "inmh":

						if not benchmark:
							test.use_for_time_benchmark = False
							test.use_for_memory_benchmark = False
							test.mandatory = True
						else:
							test.use_for_time_benchmark = True
							test.use_for_memory_benchmark = True
							test.mandatory = True
							benchmark = False

						test.type_of_feedback = 2

					# print_variables_debug([
					# 	"Test " + str(test_number) + " has:",
					# 	test.contest,
					# 	test.weight_pct,
					# 	test.mandatory,
					# 	test.use_for_memory_benchmark,
					# 	test.use_for_time_benchmark
					# ])

					test.save()
					# print_variable_debug("Test " + str(test_number) + " made!")
					# print_variable_debug(i)
			# print_variable_debug(obj)
			# print_variable_debug(a_ok)
		if a_ok:
			# print_variable_debug("Returning \"contest.get_absolute_url()\"")
			# print_variable_debug("Contest: " + str(contest))
			# print_variable_debug("URL: " + str(contest.get_absolute_url()))
			return redirect(contest.get_absolute_url())
	# obj.save()
	context = ({'form': test_form})
	# print_variable_debug("Contest: " + str(context))
	# print_variable_debug("Rendering")

	return render(request, template_name, context)


# admin test editor
@superuser_only
def admin_test_editor(request, id, t_id):
	template_name = 'contest/test_edition.html'

	contest_obj = get_object_or_404(Contest, id=id)

	test = Test.objects.filter(contest_id=id, id=t_id)

	# print_variables_debug(["Test:", test])

	context = {'test': test}

	form = TestForm(request.POST or None)

	if form.is_valid():

		print_variables_debug([
			'\n\noverride value:\n\n', request.POST.getlist('override'),
			'\n\ncpu value:\n\n', request.POST.getlist('cpu'),
			'\n\nmem value:\n\n', request.POST.getlist('mem'),
			'\n\nspace value:\n\n', request.POST.getlist('space'),
			'\n\ncore value:\n\n', request.POST.getlist('core'),
			'\n\nnproc value:\n\n', request.POST.getlist('nproc'),
			'\n\nfsize value:\n\n', request.POST.getlist('fsize'),
			'\n\nstack value:\n\n', request.POST.getlist('stack'),
			'\n\nclock value:\n\n', request.POST.getlist('clock')
		])

		if 'on' in request.POST.getlist('override'):
			test_override = True
		else:
			test_override = False
		test_cpu = request.POST.getlist('cpu')[0]
		test_mem = request.POST.getlist('mem')[0]
		test_space = request.POST.getlist('space')[0]
		test_core = request.POST.getlist('core')[0]
		test_nproc = request.POST.getlist('nproc')[0]
		test_fsize = request.POST.getlist('fsize')[0]
		test_stack = request.POST.getlist('stack')[0]
		test_clock = request.POST.getlist('clock')[0]

		print_variables_debug(["Input\n", test_override, test_cpu, test_mem, test_space, test_core, test_nproc,
							   test_fsize, test_stack, test_clock])

		test = Test.objects.get(contest_id=id, id=t_id)

		print_variables_debug(["Before\n", test.override_exec_options, test.cpu, test.mem, test.space, test.core,
							   test.nproc, test.fsize, test.stack, test.clock])

		test.override_exec_options = test_override
		test.cpu = test_cpu
		test.mem = test_mem
		test.space = test_space
		test.core = test_core
		test.nproc = test_nproc
		test.fsize = test_fsize
		test.stack = test_stack
		test.clock = test_clock
		test.save()

		print_variables_debug(["After\n", test.override_exec_options, test.cpu, test.mem, test.space, test.core,
							   test.nproc, test.fsize, test.stack, test.clock])

		return redirect(os.path.join(contest_obj.get_absolute_url(), 'admin-view/test/chooser/'))

	return render(request, template_name, context)