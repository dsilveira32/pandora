import csv
import io
import sys

from django.core.exceptions import PermissionDenied
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from shared.forms import CreateContestModelForm, TestForm, CreateTestModelForm, GroupCreateForm
from shared.models import Contest, Test, get_tests_path, Attempt
from contest.routines import *
from django.db import transaction
from .context_functions import *



def superuser_only(function):
	"""Limit view to superusers only."""
	def _inner(request, *args, **kwargs):
		if not request.user.is_superuser:
			raise PermissionDenied
		return function(request, *args, **kwargs)
	return _inner


@superuser_only
def admin_choose_test(request, id):
	template_name = 'components/tests/admin_test_chooser.html'
	contest_obj = get_object_or_404(Contest, id=id)
	context = {'contest': contest_obj}
	contest_tests = contest_obj.test_set.all()
	context.update({'tests': contest_tests})
	form = TestForm(request.POST or None)
	if form.is_valid():
		with transaction.atomic():
			mandatory_ids = request.POST.getlist('mandatory')
			check_leak_ids = request.POST.getlist('check_leak')
			contest_tests.filter(pk__in=mandatory_ids).update(mandatory = True)
			contest_tests.exclude(pk__in=mandatory_ids).update(mandatory = False)
			contest_tests.filter(pk__in=check_leak_ids).update(check_leak = True)
			contest_tests.exclude(pk__in=check_leak_ids).update(check_leak = False)

			type_of_feedback_list = request.POST.getlist('type_of_feedback')
			run_arguments_list = request.POST.getlist('run_arguments')
			weight_pct_list = request.POST.getlist('weight_pct')

			idx = 0
			for t in contest_tests:
				t.type_of_feedback = type_of_feedback_list[idx]
				t.run_arguments = run_arguments_list[idx]
				t.weight_pct = weight_pct_list[idx]

				idx = idx + 1
				t.save()

		contest_tests = contest_obj.test_set.all()
		context.update({'tests': contest_tests})
		form = TestForm()

	return render(request, template_name, context)


# admin creations
@superuser_only
def admin_contest_creation(request):
	template_name = 'contest/admin_contest_creation_form.html'

	contest_form = CreateContestModelForm(request.POST or None, request.FILES or None)
	print_form_info_debug(contest_form)
	# test_form = CreateTestModelForm(request.POST or None)
	# print("-----------------------------------The form for the test is: " + str(test_form) +
	#       "-----------------------------------")
	# print("-----------------------------------The form for the test is valid: " + str(test_form.is_valid()) +
	#       "-----------------------------------")
	if contest_form.is_valid():
		obj = contest_form.save(commit=False)
		obj.save()
		print(obj)
	# short_name = obj.short_name
	# contest_obj = get_object_or_404(Contest, short_name=short_name)
	# print(contest_obj)
	# in_files = check_in_files(obj.in_files, contest_obj)
	# out_files = check_out_files(obj.out_files, contest_obj, len(in_files))
	# create_test(request, in_files, out_files, contest_obj)
	# handle_uploaded_file(obj, obj.file, contest_obj) # to check the ins and outs files
	context = ({'form': contest_form})

	return render(request, template_name, context)


def __get_zip_file_path(zip_file):
	zip_path = os.path.abspath(zip_file.path)
	return str(os.path.dirname(zip_path)) + "/temp"



def atoi(text):
	return int(text) if text.isdigit() else text

def natural_keys(text):
	'''
	alist.sort(key=natural_keys) sorts in human order
	http://nedbatchelder.com/blog/200712/human_sorting.html
	(See Toothy's implementation in the comments)
	'''
	return [ atoi(c) for c in re.split(r'(\d+)', text) ]

@superuser_only
def admin_test_creation_old(request):
	template_name = 'pages/contest_admin.html'

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
		zip_out = obj.output_file
		# start debug
		print_variable_debug(obj.contest.short_name)
		print_variable_debug(contest)
		a_ok = True
		# end debug
		if '.zip' in str(zip_in) and '.zip' in str(zip_out):
			print_variable_debug("The files: \n" + str(zip_in).split('.')[0] + "\n" + str(zip_out).split('.')[0] +
								 "\nare zip files!")

			in_files = check_in_files(zip_in, contest)
			in_files.sort(key=natural_keys)
			print_variable_debug(in_files)
			print_variable_debug(zip_in)
			n_tests = len(in_files)
			print_variable_debug(n_tests)
			print_variable_debug(zip_out)

			#out_files = set_test_in_order(check_out_files(zip_out, contest, n_tests))

			out_files = check_out_files(zip_out, contest, n_tests)
			out_files.sort(key=natural_keys)

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
					path = __get_zip_file_path(zip_in) + "/in/" + str(in_files[i])
					f = open(path)
					test.input_file.save(in_files[i], File(f))
					f.close()
					path = __get_zip_file_path(zip_in) + "/out/" + str(out_files[i])
					f = open(path)
					print(out_files[i])
					print(f)

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
	template_name = 'contest/admin_test_edition.html'

	contest_obj = get_object_or_404(Contest, id=id)

	test = contest_obj.test_set.all()
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


		form = TestForm()
		test = contest_obj.test_set.all()

		#return redirect(os.path.join(contest_obj.get_absolute_url(), 'admin-view/test/chooser/'))

	return render(request, template_name, context)


# admin view
@superuser_only
def admin_view_old(request, id):
	template_name = 'contest/admin_team_list.html'

	contest_obj = get_object_or_404(Contest, id=id)
	context = {'contest': contest_obj}

#	teams = Team.objects.filter(contest__id=id)  # get all teams associated with this contest
	teams = contest_obj.team_set.all()

	for t in teams:
#		t.members = TeamMember.objects.filter(team=t)
		t.members = t.teammember_set.all()
		t.nMembers = t.members.count()
		t.atempts = t.atempt_set.all()
		if t.atempts:
			t.lastAtempt = t.atempts.latest('id')
			t.grade = t.lastAtempt.grade
			t.time = t.lastAtempt.time_benchmark
			t.memory = t.lastAtempt.memory_benchmark
			t.nAtempts = t.atempts.count()
		else:
			t.lastAtempt = None
			t.grade = 0
			t.time = 0
			t.memory = 0
			t.nAtempts = 0

		for m in t.members:
			m.nAtempts = t.atempts.filter(user = m.user).count()

	context.update({'teams': teams})
	"""
	form = TeamMemberForm(request.POST or None)

	if form.is_valid():
		t_id = form.cleaned_data.get("team_id")
		# verificar codigo team join e team status
		return redirect(os.path.join(contest_obj.get_absolute_url(), 'admin-view/team/' + str(t_id) + '/status/'))
	
	context.update({'form': form})
	"""
	#
	# bug = ["INFO IN THE HTML:", "***************TEAMS***********"]
	#
	# for t in teams:
	#     es = ""
	#     for e in TeamMember.objects.filter(team=t):
	#         if es == "":
	#             es = str(e.user.first_name) + " " + str(e.user.last_name)
	#         else:
	#             es += "; " + str(e.user.first_name) + " " + str(e.user.last_name)
	#     bug.append(str(t) + " - " + str(es))
	#
	# print_variables_debug(bug)

	return render(request, template_name, context)


@superuser_only
def admin_view_teams_status(request, c_id, t_id):
	template_name = 'contest/team_submission_list.html'

	contest_obj = get_object_or_404(Contest, id=c_id)
	context = {'contest': contest_obj}

	team_obj = contest_obj.getUserTeam(request.user)
	members = team_obj.getUsers()
	atempts = team_obj.getAttempts()

	if atempts:
		context.update({'number_of_submitions': atempts.count()})
		context.update({'last_classification': atempts.first().grade})
		context.update({'last_execution_time': atempts.first().time_benchmark})
		context.update({'last_memory_usage': atempts.first().memory_benchmark})
		if os.path.isfile(atempts.first().file.path):
			context.update({'download': atempts.first().file})
		else:
			context.update({'download': 0})
	else:
		context.update({'number_of_submitions': 0})
		context.update({'last_classification': 0})
		context.update({'last_execution_time': 0})
		context.update({'last_memory_usage': 0})
		context.update({'download': 0})

	team_obj.members = members
	context.update({'team': team_obj})
	context.update({'atempts': atempts})
	context.update({'maxsize': int(sys.maxsize)})

	return render(request, template_name, context)


# extract grades
@superuser_only
def extract_grades(request, id):
	print_variables_debug([request, id])
	# get the contest
	contest_obj = get_object_or_404(Contest, id=id)

	# create the HttpResponse object with the appropriate csv header.

	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename = "Contest_"' + str(
		contest_obj.id) + '""' + contest_obj.short_name + '".csv"'

	# get the values needed to be inserted in the csv
	# TODO: making this SQL sector

	query = "select ut.id, ut.number as student_number, ut.name team_name, ut.first_name, ut.last_name, gg.grade, gg.atempts as n_atempts from "\
		"	(select t.id, t.name, u.first_name, u.last_name, p.number from contest_teammember tm "\
		"		inner join contest_team t on tm.team_id = t.id "\
		"		inner join auth_user u on u.id = tm.user_id "\
		"		inner join contest_profile p on p.user_id = u.id "\
		"		WHERE t.contest_id = "+ str(contest_obj.id) +") as ut "\
		"LEFT JOIN "\
		"	(SELECT ca.grade, maxs.atempts, maxs.team_id "\
		"	FROM (select max(id) as id, count(id) as atempts, team_id from contest_atempt where contest_id = "+ str(contest_obj.id) +" group by team_id) maxs "\
		"	INNER JOIN contest_atempt ca on ca.id = maxs.id) gg "\
		"on gg.team_id = ut.id "\
		"order by team_name desc"


	grades = Attempt.objects.raw(query)

	writer = csv.writer(response, delimiter=";", dialect="excel")

	writer.writerow(['student_number', 'team_name', 'team_id', 'first_name', 'last_name', 'grade', 'n_atempts'])

	for g in grades:
		writer.writerow([g.student_number,
			g.team_name,
			g.id,
			g.first_name,
			g.last_name,
			g.grade,
			g.n_atempts])

	return response


# extract grades
@superuser_only
def extract_zip(request, id):
	# get the contest
	contest_obj = get_object_or_404(Contest, id=id)
	qs = Attempt.objects.filter(contest=contest_obj).values('team_id').annotate(id = Max('id'))
	qs2 = Attempt.objects.filter(id__in=qs.values('id'))

	zip_buffer = io.BytesIO()

	moss_str = "moss -l c -d "

	with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
		for a in qs2:
			if a.file and os.path.isfile(a.file.path):
				in_file = open(os.path.abspath(a.file.path), "rb") # opening for [r]eading as [b]inary
				data = in_file.read() # if you only wanted to read 512 bytes, do .read(512)
				in_file.close()

				fdir, fname = os.path.split(a.file.path)
				zip_path = os.path.join(a.team.name, fname)
				zip_file.writestr(zip_path, data)
				moss_str = moss_str + a.team.name + "/*.c "

		zip_file.writestr("moss.txt", moss_str)
	zip_buffer.seek(0)

	resp = HttpResponse(zip_buffer, content_type='application/zip')
	resp['Content-Disposition'] = 'attachment; filename = %s' % 'bla.zip'
	return resp



############################################
# NEW STUFF - DELETE OLD WHEN THIS IS DONE #
############################################

#############################
#         NEW VIEWS         #
#############################

# Admin contest general view (list of contests)
@superuser_only
def admin_contest_home_view(request):
	template_name = 'views/contests/admin_contests_home.html'
	context = {}
	contests = getContestsForAdmin(request)


	context.update(getAdminContestListContext(contests))
	return render(request, template_name, context)

# Admin detail contest home view
@superuser_only
def admin_contest_detail_dashboard_view(request, id):
	template_name = 'views/contests/admin_contest_detail_dashboard.html'
	context = {}
	contest = getContestByID(id)
	context.update(getAdminContestDetailLayoutContext(contest))

	# For admin_team_list.html
	teams = structureTeamsData(contest.getTeams())
	context.update(getTeamListContext(teams))

	return render(request, template_name, context)

@superuser_only
def admin_contest_detail_tests_view(request, id):
	template_name = 'views/contests/admin_contest_detail_tests.html'
	context = {}

	contest = getContestByID(id)
	contest_tests = contest.getTests()

	context.update(getAdminContestDetailLayoutContext(contest))

	context.update(getTestChooserContext(contest_tests))
	form = TestForm(request.POST or None)
	if form.is_valid():
		with transaction.atomic():
			mandatory_ids = request.POST.getlist('mandatory')
			check_leak_ids = request.POST.getlist('check_leak')
			contest_tests.filter(pk__in=mandatory_ids).update(mandatory = True)
			contest_tests.exclude(pk__in=mandatory_ids).update(mandatory = False)
			contest_tests.filter(pk__in=check_leak_ids).update(check_leak = True)
			contest_tests.exclude(pk__in=check_leak_ids).update(check_leak = False)

			type_of_feedback_list = request.POST.getlist('type_of_feedback')
			run_arguments_list = request.POST.getlist('run_arguments')
			weight_pct_list = request.POST.getlist('weight_pct')

			idx = 0
			for t in contest_tests:
				t.type_of_feedback = type_of_feedback_list[idx]
				t.run_arguments = run_arguments_list[idx]
				t.weight_pct = weight_pct_list[idx]

				idx = idx + 1
				t.save()

		contest_tests = contest.test_set.all()
		context.update(getTestChooserContext(contest_tests))
		form = TestForm()
		context.update(getContestDetailTestsContext(contest, form))
	return render(request, template_name, context)

# Admin create test view
def admin_contest_detail_tests_create_view(request, id):
	template_name = 'views/contests/admin_contest_detail_tests_create.html'
	context = {}
	contest = getContestByID(id)
	context.update(getAdminContestDetailLayoutContext(contest))

	form = CreateTestModelForm(request.POST or None, request.FILES or None)
	# TODO A melhorar
	print_form_info_debug(form)
	# test_form = CreateTestModelForm(request.POST or None)
	# print("-----------------------------------The form for the test is: " + str(test_form) +
	#       "-----------------------------------")
	# print("-----------------------------------The form for the test is valid: " + str(test_form.is_valid()) +
	#       "-----------------------------------")
	if form.is_valid():
		obj = form.save(commit=False)
		zip_in = obj.input_file
		zip_out = obj.output_file
		# start debug
		print_variable_debug(contest.short_name)
		print_variable_debug(contest)
		a_ok = True
		# end debug
		if '.zip' in str(zip_in) and '.zip' in str(zip_out):
			print_variable_debug("The files: \n" + str(zip_in).split('.')[0] + "\n" + str(zip_out).split('.')[0] +
								 "\nare zip files!")

			in_files = check_in_files(zip_in, contest)
			in_files.sort(key=natural_keys)
			print_variable_debug(in_files)
			print_variable_debug(zip_in)
			n_tests = len(in_files)
			print_variable_debug(n_tests)
			print_variable_debug(zip_out)

			# out_files = set_test_in_order(check_out_files(zip_out, contest, n_tests))

			out_files = check_out_files(zip_out, contest, n_tests)
			out_files.sort(key=natural_keys)

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
					path = __get_zip_file_path(zip_in) + "/in/" + str(in_files[i])
					f = open(path)
					test.input_file.save(in_files[i], File(f))
					f.close()
					path = __get_zip_file_path(zip_in) + "/out/" + str(out_files[i])
					f = open(path)
					print(out_files[i])
					print(f)

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


	###########################
	context.update(getTestCreationContext(contest, form))
	return render(request, template_name, context)



# Admin teams view
@superuser_only
def admin_contest_detail_teams_view(request, id):
	template_name = 'views/contests/admin_contest_detail_teams.html'
	context = {}
	contest = getContestByID(id)
	context.update(getAdminContestDetailLayoutContext(contest))

	# For admin_team_list.html
	teams = structureTeamsData(contest.getTeams())
	context.update(getTeamListContext(teams))

	return render(request, template_name, context)



####################
# 	   GROUPS	   #
####################

# Admin Groups
@superuser_only
def admin_group_home_view(request):
	template_name = 'views/groups/admin_groups_home.html'
	context = {}
	groups = getGroupsForAdmin(request)
	context.update(getAdminGroupListContext(groups))
	return render(request, template_name, context)

# Admin Groups Create
@superuser_only
def admin_group_create_view(request):
	template_name = 'views/groups/admin_groups_create.html'
	context = {}
	group_form = GroupCreateForm(request.POST or None)
	if group_form.is_valid():
		group_form.is_valid()
		group = group_form.save(commit=False)
		group.save()
	groups = getGroupsForAdmin(request)
	context.update(getAdminCreateGroupFormContext(group_form))
	context.update(getAdminGroupListContext(groups))

	return render(request, template_name, context)

# Admin Groups Detail
@superuser_only
def admin_group_detail_dashboard_view(request, id):
	template_name = 'views/groups/admin_group_detail_dashboard.html'
	context = {}
	group = getGroupByID(id)
	user_profiles = getUserProfilesFromGroup(group)
	context.update(getAdminGroupDetailLayoutContext(group))
	context.update(getAdminGroupUserListContext(user_profiles))

	return render(request, template_name, context)
