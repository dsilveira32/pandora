import os
import uuid
import subprocess
import datetime
import sys
import csv
import zipfile
from shutil import copyfile
from io import StringIO
import io
import time

from .forms import AttemptModelForm, TeamModelForm, TeamMemberForm, TeamMemberApprovalForm, \
	CreateContestModelForm, CreateTestModelForm, TestForm, ProfileEditForm, UserEditForm
from .models import Contest, Classification, Team, TeamMember, Atempt, SafeExecError, Test
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout  # last 2 imported
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files import File
from django.db.models import Max
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.encoding import smart_text
from django.views.generic.edit import FormView
from shutil import copyfile
from subprocess import check_output, CalledProcessError
from django.core.exceptions import PermissionDenied

from .utils import *

from .routines import *

def superuser_only(function):
	"""Limit view to superusers only."""
	def _inner(request, *args, **kwargs):
		if not request.user.is_superuser:
			raise PermissionDenied
		return function(request, *args, **kwargs)
	return _inner


# ---------------------------------------------- @login_required functions ---------------------------------------------
# admin choose the test to edit
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


# admin creations
@superuser_only
def admin_contest_creation(request):
	template_name = 'contest/contest_creation.html'

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
		zip_out = obj.output_file
		# start debug
		print_variable_debug(obj.contest.short_name)
		print_variable_debug(contest)
		# end debug
		if '.zip' in str(zip_in) and '.zip' in str(zip_out):
			print_variable_debug("The files: \n" + str(zip_in).split('.')[0] + "\n" + str(zip_out).split('.')[0] +
								 "\nare zip files!")
			in_files = set_test_in_order(check_in_files(zip_in, contest))
			print_variable_debug(in_files)

			print_variable_debug(zip_in)
			n_tests = len(in_files)
			print_variable_debug(n_tests)

			print_variable_debug(zip_out)
			out_files = set_test_in_order(check_out_files(zip_out, contest, n_tests))
			print_variable_debug(out_files)

			a_ok = True

			for i in range(len(in_files)):
				if not in_files[i].split('.')[0] == out_files[i].split('.')[0]:
					a_ok = False

			if a_ok:
				print_variable_debug("There is an out for each in!")
				weight = 100 / n_tests
				benchmark = False
				test_number = 0

				for i in range(n_tests):
					test_number += 1
					form = CreateTestModelForm(request.POST or None, request.FILES or None)
					test = form.save(commit=False)
					test.contest = contest
					test.weight_pct = weight
					test.input_file = in_files[i]
					test.output_file = out_files[i]
					if benchmark:
						test.use_for_time_benchmark = False
						test.use_for_memory_benchmark = False
						test.mandatory = False
					else:
						test.use_for_time_benchmark = True
						test.use_for_memory_benchmark = True
						test.mandatory = True
						benchmark = True
					print_variables_debug(["Test " + str(test_number) + " has:", test.contest, test.weight_pct,
										   test.mandatory, test.use_for_memory_benchmark, test.use_for_time_benchmark])

					test.save()
					print_variable_debug("Test " + str(test_number) + " made!")
					print_variable_debug(i)
			print(obj)

		return redirect(contest.get_absolute_url())
	# obj.save()
	context = ({'form': test_form})

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

		print_variables_debug(['\n\noverride value:\n\n', request.POST.getlist('override'),
							   '\n\ncpu value:\n\n', request.POST.getlist('cpu'),
							   '\n\nmem value:\n\n', request.POST.getlist('mem'),
							   '\n\nspace value:\n\n', request.POST.getlist('space'),
							   '\n\ncore value:\n\n', request.POST.getlist('core'),
							   '\n\nnproc value:\n\n', request.POST.getlist('nproc'),
							   '\n\nfsize value:\n\n', request.POST.getlist('fsize'),
							   '\n\nstack value:\n\n', request.POST.getlist('stack'),
							   '\n\nclock value:\n\n', request.POST.getlist('clock')])

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


# admin view
@superuser_only
def admin_view(request, id):
	template_name = 'contest/admin_view.html'

	contest_obj = get_object_or_404(Contest, id=id)
	context = {'contest': contest_obj}

	teams = Team.objects.filter(contest__id=id)  # get all teams associated with this contest

	for t in teams:
		t.members = TeamMember.objects.filter(team=t)

	context.update({'teams': teams})

	# TODO Make it better
	query = "Select ca.id, c.name as team_name, ca.grade as team_grade, maxs.atempts as team_atempts" \
			"	from (" \
			"		select max(id) as id, count(id) as atempts, team_id" \
			"			from contest_atempt" \
			"				where contest_id = " + str(contest_obj.id) + \
			"					group by team_id" \
			"	) maxs" \
			"		inner join contest_atempt ca on ca.id = maxs.id " \
			"		join contest_team c on ca.team_id = c.id" \
			"		join auth_user au on ca.user_id = au.id"

	grades = Atempt.objects.raw(query)

	context.update({'grades': grades})

	# TODO Make it better
	query = "SELECT ca.id, maxs.team_atempts, maxs.team_id, au.username as username, au.first_name, au.last_name," \
			"umax.atempts as user_atempts" \
			"	FROM (" \
			"		select max(id) as id, count(id) as team_atempts, team_id" \
			"			from contest_atempt" \
			"				where contest_id = " + str(contest_obj.id) + \
			"					group by team_id" \
			"	) maxs" \
			"		inner join contest_atempt ca on ca.id = maxs.id" \
			"		join contest_teammember ct on ct.team_id = ca.team_id" \
			"		join contest_team c on ca.team_id = c.id" \
			"		join auth_user au on au.id = ct.user_id" \
			"		join (" \
			"			select max(id) as id, count(id) as atempts, user_id" \
			"				from contest_atempt" \
			"					where contest_id = 1" \
			"						group by user_id" \
			"		) umax on umax.user_id = ct.user_id" \
			"			order by atempts asc"

	atempts = Atempt.objects.raw(query)

	context.update({'atempts': atempts})

	form = TeamMemberForm(request.POST or None)

	if form.is_valid():
		t_id = form.cleaned_data.get("team_id")
		# verificar codigo team join e team status
		return redirect(os.path.join(contest_obj.get_absolute_url(), 'admin-view/team/' + str(t_id) + '/status/'))

	context.update({'form': form})
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
	template_name = 'contest/atempt_list.html'

	contest_obj = get_object_or_404(Contest, id=c_id)
	context = {'contest': contest_obj}

	team_obj, members = get_team_members(request, contest_obj.id, t_id)

	atempts = get_team_attempts(team_obj)

	if atempts:
		context.update({'number_of_submitions': atempts.count()})
		context.update({'last_classification': atempts.first().grade})
		context.update({'last_execution_time': atempts.first().time_benchmark})
		context.update({'last_memory_usage': atempts.first().memory_benchmark})
	else:
		context.update({'number_of_submitions': 0})
		context.update({'last_classification': 0})
		context.update({'last_execution_time': 0})
		context.update({'last_memory_usage': 0})

	team_obj.members = members
	context.update({'team': team_obj})
	context.update({'atempts': atempts})
	context.update({'maxsize': int(sys.maxsize)})

	return render(request, template_name, context)


# attempt
@login_required
def attempt_list_view(request, id):
	if not request.user.profile.number:
		return redirect('complete_profile')
	if not request.user.profile.valid:
		return redirect('not_active')

	template_name = 'contest/atempt_list.html'

	contest_obj = get_object_or_404(Contest, id=id)
	context = {'contest': contest_obj}

	team_obj, members = get_user_team(request, contest_obj.id)
	if not team_obj:
		return redirect(os.path.join(contest_obj.get_absolute_url(), 'team/join/'))

	atempts = get_team_attempts(team_obj)

	if atempts:
		context.update({'number_of_submitions': atempts.count()})
		context.update({'last_classification': atempts.first().grade})
		context.update({'last_execution_time': atempts.first().time_benchmark})
		context.update({'last_memory_usage': atempts.first().memory_benchmark})
	else:
		context.update({'number_of_submitions': 0})
		context.update({'last_classification': 0})
		context.update({'last_execution_time': int(sys.maxsize)})
		context.update({'last_memory_usage': int(sys.maxsize)})

	team_obj.members = members
	context.update({'team': team_obj})
	context.update({'atempts': atempts})
	context.update({'title': "Status"})

	return render(request, template_name, context)


@login_required
def attempt_view(request, id):
	if not request.user.profile.number:
		return redirect('complete_profile')
	if not request.user.profile.valid:
		return redirect('not_active')

	template_name = 'contest/atempt_detail.html'

	atempt_obj = get_object_or_404(Atempt, id=id)
	contest_obj = atempt_obj.contest
	team = atempt_obj.team

	# check if request.user is a member of atempt team OR admin
	if not team.teammember_set.filter(user=request.user, approved = True) and not request.user.is_superuser:
		raise Http404

	results = atempt_obj.classification_set.all()
	n_tests = contest_obj.test_set.count()
	n_mandatory = contest_obj.test_set.filter(mandatory=True).count()
	n_general = n_tests - n_mandatory
	n_passed = atempt_obj.classification_set.filter(passed=True).count()
	mandatory_passed = atempt_obj.classification_set.filter(passed=True, test__mandatory=True).count()
	general_passed = atempt_obj.classification_set.filter(passed=True, test__mandatory=False).count()

#	print('number of results ' + str(results.count()))
#	print('number of tests ' + str(n_tests))
#	print('number of mandatory tests ' + str(n_mandatory))
#	print('number of general tests ' + str(n_general))
#	print('number of general passed tests ' + str(general_passed))
#	print('number of mandatory passed tests ' + str(mandatory_passed))

	for res in results:
		res.expected_output = smart_text(res.test.output_file.read(), encoding='utf-8', strings_only=False,
										 errors='strict')
		if res.output and os.path.isfile(res.output.path):
			res.obtained_output = smart_text(res.output.read(), encoding='utf-8', strings_only=False, errors='strict')
		else:
			res.obtained_output = ''


	context = {'contest': contest_obj}
	context.update({'team': team})
	context.update({'team_members': team.teammember_set.all()})
	context.update({'atempt': atempt_obj})
	context.update({'maxsize': 2147483647})
	context.update({'n_passed': n_passed})
	context.update({'n_total': n_tests})
	context.update({'mandatory_passed': mandatory_passed})
	context.update({'mandatory_total': n_mandatory})
	context.update({'general_passed': general_passed})
	context.update({'n_general': n_general})
	context.update({'results': results})
	context.update({'title': "Atempt Detail"})
	return render(request, template_name, context)


@login_required
def attempt_create_view(request, id):
	if not request.user.profile.number:
		return redirect('complete_profile')
	if not request.user.profile.valid:
		return redirect('not_active')

	template_name = 'contest/contest_form.html'
	contest_obj = get_object_or_404(Contest, id=id)
	context = {'contest': contest_obj}
	can_submit = True

	present = timezone.now()
	# present = datetime.datetime.now()
	if present < contest_obj.start_date or present > contest_obj.end_date:
		# contest is not opened
		return redirect(os.path.join(contest_obj.get_absolute_url()))

	team_obj, members = get_user_team(request, contest_obj.id)
	if not team_obj:
		if contest_obj.max_team_members == 1:
			team_obj = Team(name=request.user.username, contest=contest_obj)
			team_obj.save()
			tm = TeamMember(team = team_obj, user=request.user, approved=True)
			tm.save()
			members = team_obj.teammember_set.all()
		else:
			return redirect(os.path.join(contest_obj.get_absolute_url(), 'team/join/'))

	atempts = get_team_attempts(team_obj)

	if contest_obj.max_submitions > 0:
		if atempts and atempts.count() >= contest_obj.max_submitions:
			messages.error(request, "You have reached the maximum number of submitions for this contest.")
			can_submit = False

	if not contest_obj.is_open:
		messages.error(request, "This contest is not active.")
		can_submit = False

	if not team_obj.active or not members.filter(user=request.user).first().approved or not request.user.profile.valid:
		messages.error(request,
					   "You need to be an Active member and approved member of an active team to make submitions")
		can_submit = False

	form = AttemptModelForm(request.POST or None, request.FILES or None)
	if can_submit and form.is_valid():
		obj = form.save(commit=False)
		obj.user = request.user
		obj.contest = contest_obj
		obj.team = team_obj
		obj.save()
		handle_uploaded_file(obj, obj.file, contest_obj)
		return redirect(obj.get_absolute_url())

	context.update({'form': form, 'title': "Submit"})
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


	grades = Atempt.objects.raw(query)

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
	qs = Atempt.objects.filter(contest=contest_obj).values('team_id').annotate(id = Max('id'))
	qs2 = Atempt.objects.filter(id__in=qs.values('id'))

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
				moss_str = moss_str + zip_path + "/*.c "

			zip_file.writestr("moss.txt", moss_str)

	zip_buffer.seek(0)

	resp = HttpResponse(zip_buffer, content_type='application/zip')
	resp['Content-Disposition'] = 'attachment; filename = %s' % 'bla.zip'
	return resp


# contest
@login_required
def contest_list_view(request):
	if not request.user.profile.number:
		return redirect('complete_profile')
	if not request.user.profile.valid:
		return redirect('not_active')

	template_name = 'contest/list.html'

	if request.user.is_superuser:
		contests_qs = Contest.objects.all()
	else:
		contests_qs = Contest.objects.filter(visible=True)

	qs = TeamMember.objects.select_related('team').filter(user=request.user)

	context = {'object_list': contests_qs,
			   'team_contests': qs,
			   'title': 'Contests',
			   'description': 'PANDORA is an Automated Assement Tool.'}
	return render(request, template_name, context)


@login_required
def contest_detail_view(request, id):
	if not request.user.profile.number:
		return redirect('complete_profile')
	if not request.user.profile.valid:
		return redirect('not_active')

	obj = get_object_or_404(Contest, id=id)

	present = timezone.now()
	if present < obj.start_date:
		# contest is not yet open. Don't let anyone see a dam thing.
		template_name = 'contest/closed.html'
	else:
		template_name = 'contest/detail.html'

	context = {"contest": obj}
	return render(request, template_name, context)


# profile
@login_required
def profile_view(request):
	template_name = 'contest/profile.html'
	context = {'user': request.user, 'title': "My Information"}
	return render(request, template_name, context)


# ranking
@login_required
def ranking_view(request, id):
	if not request.user.profile.number:
		return redirect('complete_profile')
	if not request.user.profile.valid:
		return redirect('not_active')

	template_name = 'contest/ranking.html'


	contest_obj = get_object_or_404(Contest, id=id)
	context = {'contest': contest_obj}

	# TODO Make it better
	query = "SELECT ca.*, maxs.atempts, maxs.team_id FROM (" \
			"select max(id) as id," \
			"count(id) as atempts," \
			"team_id from " \
			"contest_atempt" \
			" where contest_id = " + str(contest_obj.id) + \
			"   group by team_id)" \
			"       maxs inner join contest_atempt ca on ca.id = maxs.id" \
			"           order by grade desc, atempts asc, time_benchmark asc, memory_benchmark asc, elapsed_time asc," \
			"                       cpu_time asc"
	# select contest_atempt.id as id, max(date), grade, count(contest_atempt.id) as number_of_atempts, time_benchmark, memory_benchmark elapsed_time, cpu_time from contest_atempt where contest_id = " + str(contest_obj.id) + " group by (team_id) order by grade desc, time_benchmark asc, memory_benchmark asc, number_of_atempts asc"

	atempts = Atempt.objects.raw(query)

	context.update({'atempts': atempts})
	context.update({'title': "Ranking"})
	return render(request, template_name, context)


# team
@login_required
def team_create_view(request, id):
	if not request.user.profile.number:
		return redirect('complete_profile')
	if not request.user.profile.valid:
		return redirect('not_active')

	template_name = 'contest/contest_form.html'
	contest_obj = get_object_or_404(Contest, id=id)
	context = {'contest': contest_obj}

	user_team = TeamMember.objects.select_related('team').filter(team__contest=contest_obj.id,
																 user=request.user).first()

	if user_team:
		# this user already has a team
		return redirect(os.path.join(contest_obj.get_absolute_url(), 'myteam/'))

	# in case individual submition - Create a team with the username with only one member
	if contest_obj.max_team_members == 1:
		t = Team(name=request.user.username, contest=contest_obj)
		t.save()
		tm = TeamMember(team = t, user=request.user, approved=True)
		tm.save()
		return redirect(os.path.join(contest_obj.get_absolute_url(), 'myteam/'))

	form = TeamModelForm(request.POST or None)
	if form.is_valid():
		obj = form.save(commit=False)
		obj.contest = contest_obj
		obj.save()
		team_member_obj = TeamMember()
		team_member_obj.user = request.user
		team_member_obj.approved = True
		team_member_obj.team = obj
		team_member_obj.save()
		return redirect(os.path.join(contest_obj.get_absolute_url(), 'myteam/'))

	context.update({'form': form})
	context.update({"title": 'Create New Team'})
	return render(request, template_name, context)


@login_required
def team_detail_view(request, id):
	if not request.user.profile.number:
		return redirect('complete_profile')
	if not request.user.profile.valid:
		return redirect('not_active')


	template_name = 'contest/team_detail.html'

	contest_obj = get_object_or_404(Contest, id=id)
	context = {'contest': contest_obj}

	# qs = TeamMember.objects.select_related('team').filter(team__contest = contest_obj.id, user = request.user).first()
	team_obj, members = get_user_team(request, contest_obj.id)
	if not team_obj:
		return redirect(os.path.join(contest_obj.get_absolute_url(), 'team/join/'))

	team_member_obj = TeamMember.objects.get(team=team_obj, user=request.user)

	can_be_deleted = True
	if members.count() > 1 or not team_member_obj.approved or get_team_attempts(team_obj):
		can_be_deleted = False

	form = TeamMemberApprovalForm(request.POST or None)
	if form.is_valid():
		if "team_delete" in request.POST and can_be_deleted:
			team_member_obj.delete()
			team_obj.delete()
			return redirect(os.path.join(contest_obj.get_absolute_url(), 'team/join/'))

		if team_member_obj.approved:
			if "member_id" in request.POST:
				team_member_obj2 = TeamMember.objects.get(id=form.cleaned_data.get("member_id"))
				team_member_obj2.approved = True
				team_member_obj2.save()

		if members.count() > 1 and "member_id_remove" in request.POST:
			team_member_obj2 = TeamMember.objects.get(id=form.cleaned_data.get("member_id_remove"))
			if (team_member_obj2 == team_member_obj and not team_member_obj2.approved) or team_member_obj.approved:
				team_member_obj2.delete()
				return redirect(os.path.join(contest_obj.get_absolute_url(), 'team/join/'))

		form = TeamMemberApprovalForm()
		team_obj.members = team_obj.teammember_set.all()

	team_obj.members = team_obj.teammember_set.all()

	context.update({'team': team_obj})
	context.update({'can_delete': can_be_deleted})  # it it only has one member, it can be deleted
	context.update({'can_approve': team_member_obj.approved})  # it it only has one member, it can be deleted
	context.update({'form': form})
	return render(request, template_name, context)


@login_required
def team_join_view(request, id):
	if not request.user.profile.number:
		return redirect('complete_profile')
	if not request.user.profile.valid:
		return redirect('not_active')

	template_name = 'contest/team_join.html'
	contest_obj = get_object_or_404(Contest, id=id)
	context = {'contest': contest_obj}

	user_team, members = get_user_team(request, contest_obj.id)
	user_team.members = members
	# TeamMember.objects.select_related('team').filter(team__contest = contest_obj.id, user = request.user).first()

	if user_team:
		return redirect(os.path.join(contest_obj.get_absolute_url(), 'myteam/'))

	# in case individual submition - Create a team with the username with only one member
	if contest_obj.max_team_members == 1:
		t = Team(name=request.user.username, contest=contest_obj)
		t.save()
		tm = TeamMember(team = t, user=request.user, approved=True)
		tm.save()
		return redirect(os.path.join(contest_obj.get_absolute_url(), 'myteam/'))

	# get all teams active in this contenst
	teams = Team.objects.filter(contest__id=id)  # get all teams associated with this contest

	# set the members details and the amount of new member that can join
	for obj in teams:
		obj.members = TeamMember.objects.filter(team=obj)
		obj.room_left = obj.contest.max_team_members - obj.members.count()

	# update the contenxt to send to the team_join.html
	context.update({'teams': teams})

	# no idea what it does
	form = TeamMemberForm(request.POST or None)

	if form.is_valid():
		team_id = form.cleaned_data.get("team_id")
		team_member = TeamMember()

		team = Team.objects.get(id=team_id)

		qs = team.teammember_set.all()
		if qs.count() > team.contest.max_team_members:
			messages.error(request, "Error! This team can not accept new members")
		else:
			team_member.team = team
			team_member.user = request.user
			team_member.approved = False
			team_member.save()
			return redirect(os.path.join(contest_obj.get_absolute_url(), 'myteam/'))
		form = TeamMemberForm()

	# context.update({'form': form})
	return render(request, template_name, context)


# ------------------------------------------------------ The rest ------------------------------------------------------
# page logout
def pagelogout(request):
	if request.method == "POST":
		logout(request)
		return redirect('home')


# non active view
def nonactive_view(request):
	template_name = 'contest/error.html'
	context = {'title': 'Not active',
			   'description': 'Your account is not active. Please wait for the administrator to activate your account.'}
	return render(request, template_name, context)


@login_required
def complete_profile_view(request):
	profile_form = ProfileEditForm(request.POST or None, instance = request.user.profile)
	user_form = UserEditForm(request.POST or None, instance = request.user)
	
	if all((profile_form.is_valid(), user_form.is_valid())):
		profile_form.save()
		user_form.save()
		return redirect('home')
	else:
		user_form = UserEditForm(request.POST or None, instance = request.user)
		profile_form = ProfileEditForm(request.POST or None, instance = request.user.profile)

	context = {'form': user_form,
				'form2': profile_form,
				'title': 'Complete Information'}
	return render(request, 'form.html', context)


@login_required
def home_view(request):
	template_name = 'contest/dashboard.html'
	context = {'title': "Dashboard"}
	return render(request, template_name, context)



	