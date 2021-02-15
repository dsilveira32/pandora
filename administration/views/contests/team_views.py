from administration.views.general import superuser_only
from django.shortcuts import render
from administration.context_functions import *
from shared.models import Team
from shared.routines import *
# Admin teams dashboard view
from user.views.contest_views import user_has_contest

# TODO: create user_has_team decorator

@superuser_only
@user_has_contest
def dashboard_view(request, contest_id):
	template_name = 'admin/views/contests/teams/dashboard.html'
	context = {}
	contest = getContestByID(contest_id)
	context.update(getAdminContestDetailLayoutContext(contest))

	# For list.html
	teams = structureTeamsData(contest.getTeams())
	context.update(getAdminTeamListContext(teams))

	return render(request, template_name, context)


# Admin team detail dashboard view
@superuser_only
@user_has_contest
def detail_dashboard_view(request, contest_id, team_id):
	template_name = 'admin/views/contests/teams/admin_contest_detail_team_edit.html'
	context = {}
	contest = getContestByID(contest_id)
	context.update(getAdminContestDetailLayoutContext(contest))
	team = Team.objects.filter(id=team_id).first()
	context.update(getAdminTeamDetailContext(team))


	return render(request, template_name, context)
