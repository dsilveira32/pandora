from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from shared.models import Team
from shared.routines import *
from shared.forms import TeamJoinForm, TeamCreateForm
from user.context_functions import *
from user.views import contest_views
from user.views.general import user_approval_required, user_complete_profile_required


def user_has_team(function):
    """Limit view to users that belong to a team in that contest."""

    def _inner(request, *args, **kwargs):
        contest_id = kwargs.get('contest_id')
        contest = Contest.getByID(contest_id)
        team = contest.getUserTeam(request.user)
        if team:
            return function(request, *args, **kwargs)
        raise PermissionDenied

    return _inner


def user_belongs_to_team(function):
    """Limit view to users that belong to the team."""

    def _inner(request, *args, **kwargs):
        team_id = kwargs.get('team_id')
        team = Team.getById(team_id)
        if team:
               if team.hasUser(request.user):
                   return function(request, *args, **kwargs)
        raise PermissionDenied

    return _inner


@login_required
@user_complete_profile_required
@user_approval_required
def join_view(request, contest_id):
    context = {}
    template_name = 'user/views/contests/teams/join.html'

    contest = getContestByID(contest_id)

    join_form = TeamJoinForm(request.POST or None if 'submit_join_form' in request.POST else None)
    if join_form.is_valid():
        if join_form.submit(request.user, contest):
            return redirect(contest_views.detail_dashboard_view, contest_id)


    create_form = TeamCreateForm(request.POST or None if 'submit_create_form' in request.POST else None)
    if create_form.is_valid():
        if create_form.submit(request.user, contest):
            return redirect(contest_views.detail_dashboard_view, contest_id)

    context.update(getContestDetailLayoutContext(contest))
    context.update(getTeamJoinFormContext(create_form, join_form))
    return render(request, template_name, context)


@login_required
@user_complete_profile_required
@user_approval_required
@user_belongs_to_team
def detail_dashboard_view(request, team_id):
    template_name = 'doesnt_exist_yet.html'

    context = {}
    return render(request, template_name, context)