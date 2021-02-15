from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from shared.routines import *
from user.context_functions import *
from user.views.general import user_approval_required

def user_has_contest(function):
    """Limit view to users that have access to the contest."""

    def _inner(request, *args, **kwargs):
        contest_id = kwargs.get('contest_id')
        contest = Contest.getContestByID(contest_id)
        if contest:
               if contest.userHasAccess(request.user):
                   return function(request, *args, **kwargs)
        raise PermissionDenied

    return _inner


# HOME VIEW

@login_required
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
@user_approval_required
@user_has_contest
def detail_dashboard_view(request, contest_id):
    #checkUserProfileInRequest(request)
    context = {}
    template_name = 'user/views/contests/detail_dashboard.html'

    # Get required data
    contest = getContestByID(contest_id)
    team = contest.getUserTeam(request.user)

    if team:
        team_attempts = team.getAttempts()
        context.update(getTeamSubmissionStatusContext(team_attempts))
        context.update(getTeamSubmissionHistoryContext(team_attempts))

        ranked_attempts = getAllContestAttemptsRanking(contest)
        context.update(getContestRankingsContext(ranked_attempts))


    # Update context
    print_variable_debug(team)
    context.update(getContestDetailLayoutContext(contest))
    context.update(getTeamMembersContext(team))
    context.update(getContestDetailsContext(contest))
    context.update(getContestSubmitAttemptButton(contest, team))
    return render(request, template_name, context)



