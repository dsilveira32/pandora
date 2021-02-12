from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from shared.forms import TeamJoinForm, TeamCreateForm
from user.context_functions import *
from user.views import contest_views


# TEAM JOIN VIEW
@login_required
def join_view(request, contest_id):
    context = {}
    template_name = 'user/views/contests/teams/join.html'

    contest = getContestByID(id)

    join_form = TeamJoinForm(request.POST or None if 'submit_join_form' in request.POST else None)
    if join_form.is_valid():
        if join_form.submit(request.user, contest):
            return redirect(contest_views.detail_dashboard_view, id)


    create_form = TeamCreateForm(request.POST or None if 'submit_create_form' in request.POST else None)
    if create_form.is_valid():
        if create_form.submit(request.user, contest):
            return redirect(contest_views.detail_dashboard_view, id)

    context.update(getContestDetailLayoutContext(contest))
    context.update(getTeamJoinFormContext(create_form, join_form))
    return render(request, template_name, context)


@login_required
def detail_dashboard_view(request, team_id):
    template_name = 'doesnt_exist_yet.html'

    context = {}
    return render(request, template_name, context)