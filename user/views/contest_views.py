import io

from coolname import generate_slug
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render
from shared.routines import *
from user.context_functions import *
from shared.models import Team
from user.views.general import user_approval_required, user_complete_profile_required
import uuid


def contest_is_open(function):
    """Block view when the contest is closed."""

    def _inner(request, *args, **kwargs):
        contest_id = kwargs.get('contest_id')
        contest = Contest.getByID(contest_id)
        if contest:
            if contest.isOpen():
                return function(request, *args, **kwargs)
        raise PermissionDenied

    return _inner


def user_has_access_to_contest(function):
    """Limit view to users that have access to the contest."""

    def _inner(request, *args, **kwargs):
        contest_id = kwargs.get('contest_id')
        contest = Contest.getByID(contest_id)
        if contest:
            if contest.userHasAccess(request.user):
                return function(request, *args, **kwargs)
        raise PermissionDenied

    return _inner


def submission_limit_not_reached(function):
    """Limit view to users whose team has not reached the submission limit"""

    def _inner(request, *args, **kwargs):
        contest_id = kwargs.get('contest_id')
        contest = Contest.getByID(contest_id)
        user = request.user
        team = contest.getUserTeam(user)
        attempt_count = team.getAttempts().count() or 0
        if contest.max_submitions == 0 or attempt_count < contest.max_submitions:
            return function(request, *args, **kwargs)
        raise PermissionDenied

    return _inner


# HOME VIEW

@login_required
@user_complete_profile_required
@user_approval_required
def dashboard_view(request):
    template_name = 'user/views/contests/dashboard.html'
    context = {'title': 'Contests',
               'description': 'PANDORA is an Automated Assessment Tool.',
               # TODO: FIND OUT WHAT THIS WAS FOR - PERG AO PROF 'team_contests': getTeamContests(request),
               }
    contests = Contest.getContestsForUser(request)
    context.update(getContestListContext(contests))
    return render(request, template_name, context)


# CONTEST VIEW
@login_required
@user_complete_profile_required
@user_approval_required
@user_has_access_to_contest
def detail_dashboard_view(request, contest_id):
    context = {}
    template_name = 'user/views/contests/detail_dashboard.html'

    # Get required data
    contest = getContestByID(contest_id)
    team = contest.getUserTeam(request.user)

    if not team and contest.max_team_members == 1:
        team = Team(name=generate_slug(2), contest=contest, join_code=request.user.username)
        team.save()
        team.users.add(request.user)
        team.save()

    if team:
        team_attempts = team.getAttempts()
        context.update(getTeamSubmissionStatusContext(team_attempts, contest))
        context.update(getTeamSubmissionHistoryContext(team_attempts))
        context.update(getUserContestsSubmissionsLeftContext(contest, team_attempts))
        team_attempt, rank = getAllContestAttemptsSingleRanking(contest, team)
        context.update(getContestSingleRankingContext(team_attempt, rank))

    # Update context
    print_variable_debug(team)
    context.update(getContestDetailLayoutContext(contest))
    context.update(getTeamMembersContext(team))
    context.update(getContestDetailsContext(contest))
    context.update(getContestSubmitAttemptButton(contest, team))
    context.update(getUserContestGradeProgressContext(request, contest))
    return render(request, template_name, context)
