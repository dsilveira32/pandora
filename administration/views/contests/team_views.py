from administration.views.general import superuser_only
from django.shortcuts import render
from administration.context_functions import *
from shared.forms import TeamModelForm, AdminTeamCreateForm, AdminTeamEditForm, AdminTeamManagerForm, \
	TeamDateExceptionForm
from shared.models import Team
from shared.routines import *
# Admin teams dashboard view


@superuser_only
def dashboard_view(request, contest_id):
	template_name = 'admin/pages/contests/teams/dashboard.html'
	context = {}
	contest = getContestByID(contest_id)

	# For list.html
	teams = structureTeamsData(contest.getTeams())

	context.update(getAdminTeamNonDetailLayoutContext(contest))
	context.update(getAdminTeamListContext(teams))

	return render(request, template_name, context)




# Admin team detail dashboard view
@superuser_only
def create_view(request, contest_id):
	template_name = 'admin/pages/contests/teams/create.html'
	context = {}
	contest = getContestByID(contest_id)
	form = AdminTeamCreateForm(request.POST or None)
	if form.is_valid():
		if form.submit(request.user, contest):
			return redirect("manager_contests_detail_teams", contest_id=contest_id)
	context.update(getAdminContestsTeamsFormContext(form))
	context.update(getAdminTeamNonDetailLayoutContext(contest))
	return render(request, template_name, context)

# Admin team detail dashboard view
@superuser_only
def detail_view(request, contest_id, team_id):
	template_name = 'admin/pages/contests/teams/detail.html'
	context = {}
	contest = getContestByID(contest_id)
	team = Team.getById(team_id)
	submissions = team.getAttempts()
	date_exception = team.getDateException()
	if date_exception:
		form = TeamDateExceptionForm(request.POST or None, instance=date_exception)
	else:
		form = TeamDateExceptionForm(request.POST or None)
	form.submit(team)
	context.update(getAdminTeamDetailLayoutContext(contest, team))
	context.update(getAdminContestsTeamsDetailContext(team))
	context.update(getAdminContestSubmissionListContext(submissions))
	context.update(getAdminTeamDateExceptionFormContext(form))
	return render(request, template_name, context)


# Admin team detail dashboard view
@superuser_only
def edit_view(request, contest_id, team_id):
	template_name = 'admin/pages/contests/teams/edit.html'
	context = {}
	contest = getContestByID(contest_id)
	team = Team.getById(team_id)

	users_out = contest.getUsers().exclude(team__users__team__exact=team)

	form = AdminTeamEditForm(instance=team)
	form_manager = AdminTeamManagerForm(request.POST or None)

	if not 'action' in request.POST:
		form = AdminTeamEditForm(request.POST or None, instance=team)
		if form.is_valid():
			if form.submit(request.user, contest):
				return redirect("manager_contests_detail_teams", contest_id=contest_id)
	else:
		if form_manager.is_valid():
			form_manager.submit(team)

	context.update(getAdminTeamDetailLayoutContext(contest, team))
	context.update(getAdminContestsTeamsFormContext(form))
	context.update(getAdminContestsTeamsManagerContext(users_out, team.getUsers(), team))
	return render(request, template_name, context)
