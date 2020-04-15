import datetime
import os
import shutil
import subprocess
import sys
from shutil import copyfile
from subprocess import check_output

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.encoding import smart_text

from contest.forms import AttemptModelForm, TeamModelForm, TeamMemberForm, TeamMemberApprovalForm, \
	ProfileEditForm, UserEditForm
from contest.models import Classification, Team, TeamMember, Atempt, SafeExecError
from contest.models import Contest, UserContestDateException
from contest.utils import *


# ------------------------------------------------------ routines ------------------------------------------------------
def get_test_contest_details(t_c):
	return t_c.cpu, t_c.mem, t_c.space, t_c.minuid, t_c.maxuid, t_c.core, t_c.nproc, t_c.fsize, t_c.stack, t_c.clock


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


def handle_uploaded_file(attempt, f, contest):
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
		handle_zip_file(attempt, f, contest)

	print('source path = ' + src_path)

	submition_dir = os.path.dirname(src_path)
	# obj_file = submition_dir + '/' + src_name + '.user.o'
	obj_file = src_name + '.user.o'

	# print('submition dir = ' + submition_dir)

	attempt.compile_error = False
	# my_cmd = 'gcc ' + contest.compile_flags + ' ' + src_base + ' -o ' + obj_file + ' ' + contest.linkage_flags
	my_cmd = 'gcc ' + contest.compile_flags + ' ' + '*.c ' + ' -I ' + './src/*.c ' + ' -o ' + obj_file + ' ' +\
		contest.linkage_flags
	# my_cmd = 'gcc ' + contest.compile_flags + ' ' + submition_dir + '/*.c ' + ' -I ' + submition_dir + '/src/*.c ' +
	# ' -o ' + obj_file + ' ' + contest.linkage_flags

	print('compilation: ' + my_cmd)
	output, ret = check_output(my_cmd, submition_dir)

	if output[0] != '':
		attempt.compile_error = True
		attempt.error_description = output[0]
		print('compile error... terminating...')
		attempt.save()
		return  # if compilation errors or warnings dont bother with running the tests

	chmod_cmd = "chmod a+w " + submition_dir
	output, ret = check_output(chmod_cmd, submition_dir)
	print_variables_debug([output, ret])

	test_set = contest.test_set.all()

	n_tests = test_set.count()
	mandatory_failed = False
	pct = 0
	attempt.time_benchmark = 0
	attempt.memory_benchmark = 0
	attempt.cpu_time = 0
	attempt.elapsed_time = 0

	for test in test_set:
		record = Classification()
		record.attempt = attempt
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
			attempt.memory_benchmark += record.memory_usage
			attempt.time_benchmark += record.execution_time
			attempt.cpu_time += record.cpu_time
			attempt.elapsed_time += record.elapsed_time

			if test.use_for_memory_benchmark:
				attempt.memory_benchmark = record.memory_usage
		else:
			record.error_description = 'Wrong Answer'

			if test.mandatory:
				mandatory_failed = True
		record.save()
		os.remove(user_output)

	attempt.grade = (round(pct / 100 * contest.max_classification, 0), 0)[mandatory_failed]
	attempt.save()
	os.remove(os.path.join(submition_dir, obj_file))
	cleanup_past_attempts(attempt.team, attempt)


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


# -------------------------------------------------- log in functions --------------------------------------------------
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

	start_date = contest_obj.start_date
	end_date = contest_obj.end_date

	# this is to allow specific users to submit outside the scheduled dates
	# example is a user that was sick
	try:
		user_excep = UserContestDateException.objects.get(user = request.user, contest = contest_obj)
	except UserContestDateException.DoesNotExist:
		user_excep = None
	if user_excep:
		start_date = user_excep.start_date
		end_date = user_excep.end_date

	present = timezone.now()
	# present = datetime.datetime.now()
	if not request.user.is_superuser:
		if present < start_date or present > end_date:
			# contest is not opened
			return redirect(os.path.join(contest_obj.get_absolute_url()))

	team_obj, members = get_user_team(request, contest_obj.id)
	if not team_obj:
		if contest_obj.max_team_members == 1:
			team_obj = Team(name=request.user.username, contest=contest_obj)
			team_obj.save()
			tm = TeamMember(team=team_obj, user=request.user, approved=True)
			tm.save()
			members = team_obj.teammember_set.all()
		else:
			return redirect(os.path.join(contest_obj.get_absolute_url(), 'team/join/'))

	atempts = get_team_attempts(team_obj)

	if contest_obj.max_submitions > 0:
		if atempts and atempts.count() >= contest_obj.max_submitions:
			messages.error(request, "You have reached the maximum number of submissions for this contest.")
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
		print_variables_debug([
			"Object: " + str(obj),
			"Object file: " + str(obj.file),
			"Object file path: " + str(obj.file.path),
			"Contest object: " + str(contest_obj)
		])
		handle_uploaded_file(obj, obj.file, contest_obj)
		return redirect(obj.get_absolute_url())

	context.update({'form': form, 'title': "Submit"})
	return render(request, template_name, context)


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
		return redirect(os.path.join(contest_obj.get_absolute_url(), 'my_team/'))

	# in case individual submition - Create a team with the username with only one member
	if contest_obj.max_team_members == 1:
		t = Team(name=request.user.username, contest=contest_obj)
		t.save()
		tm = TeamMember(team = t, user=request.user, approved=True)
		tm.save()
		return redirect(os.path.join(contest_obj.get_absolute_url(), 'my_team/'))

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
		return redirect(os.path.join(contest_obj.get_absolute_url(), 'my_team/'))

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
		return redirect(os.path.join(contest_obj.get_absolute_url(), 'my_team/'))

	# in case individual submition - Create a team with the username with only one member
	if contest_obj.max_team_members == 1:
		t = Team(name=request.user.username, contest=contest_obj)
		t.save()
		tm = TeamMember(team = t, user=request.user, approved=True)
		tm.save()
		return redirect(os.path.join(contest_obj.get_absolute_url(), 'my_team/'))

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
			return redirect(os.path.join(contest_obj.get_absolute_url(), 'my_team/'))
		form = TeamMemberForm()

	# context.update({'form': form})
	return render(request, template_name, context)


@login_required
def complete_profile_view(request):
	profile_form = ProfileEditForm(request.POST or None, instance=request.user.profile)
	user_form = UserEditForm(request.POST or None, instance=request.user)

	if all((profile_form.is_valid(), user_form.is_valid())):
		profile_form.save()
		user_form.save()
		return redirect('home')
	else:
		user_form = UserEditForm(request.POST or None, instance=request.user)
		profile_form = ProfileEditForm(request.POST or None, instance=request.user.profile)

	context = {
		'form': user_form,
		'form2': profile_form,
		'title': 'Complete Information'
	}
	return render(request, 'form.html', context)


@login_required
def home_view(request):
	template_name = 'contest/dashboard.html'
	context = {'title': "Dashboard"}
	return render(request, template_name, context)