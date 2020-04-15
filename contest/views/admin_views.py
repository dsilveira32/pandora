import csv
import io
import os
import sys
import zipfile

from django.core.exceptions import PermissionDenied
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from contest.forms import TeamMemberForm, CreateContestModelForm
from contest.models import Contest
from contest.models import Team, TeamMember, Atempt
from contest.utils import *


# ------------------------------------------------------ routines ------------------------------------------------------
def superuser_only(function):
	"""Limit view to superusers only."""
	def _inner(request, *args, **kwargs):
		if not request.user.is_superuser:
			raise PermissionDenied
		return function(request, *args, **kwargs)
	return _inner


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


# get the team attempts
def get_team_attempts(team):
	members_ids = team.teammember_set.values_list('user__id', flat=True).distinct()
	if not members_ids:
		return None

	return Atempt.objects.filter(contest=team.contest, user__in=members_ids).order_by('-date')


# ------------------------------------------------ super user function--------------------------------------------------
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
				moss_str = moss_str + a.team.name + "/*.c "

		zip_file.writestr("moss.txt", moss_str)
	zip_buffer.seek(0)

	resp = HttpResponse(zip_buffer, content_type='application/zip')
	resp['Content-Disposition'] = 'attachment; filename = %s' % 'bla.zip'
	return resp