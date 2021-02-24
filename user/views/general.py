from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from shared.routines import *
from shared.forms import ProfileEditForm, UserEditForm
from user.context_functions import *
from user.views import contest_views


def user_approval_required(function):
    """
    Limit view to users have property active set to true.
    i.e. users that have been approved by the admin
    """

    def _inner(request, *args, **kwargs):
        if request.user.profile.valid:
            return function(request, *args, **kwargs)
        return redirect(awaiting_approval_view)

    return _inner



@login_required
@user_approval_required
def dashboard_view(request):
    return redirect(contest_views.dashboard_view)
    template_name = 'user/views/dashboard.html'
    context = {}
    contests = getContestsForUser(request)
    labels = []
    data = []
    bgcolors = []
    if contests:
        for contest in contests:
            labels.append(contest.getName())
            team = contest.getUserTeam(request.user)
            if team:
                submission = team.getGreatestGradeAttempt()
                if submission:
                    data.append(submission.getGrade())
                    bgcolors.append('#4e73df')

    numberOpenedContests = 0
    for contest in getContestsForUser(request):
        if (contest.isOpen()):
            numberOpenedContests += 1

    context.update(getUserGradesDasboardContext(labels, [
        {
            'label': 'Nota',
            'data': data,
            'backgroundColor': bgcolors,
            'hoverBackgroundColor': "#2e59d9",
            'borderColor': "#4e73df"
        }
    ]))

    context.update(getUserContestsNumberCardContext(numberOpenedContests))
    return render(request, template_name, context)


@login_required
def profile_view(request):
    template_name = 'user/views/profile.html'
    context = {}
    profile_form = ProfileEditForm(request.POST or None, instance=request.user.profile)
    user_form = UserEditForm(request.POST or None, instance=request.user)

    if all((profile_form.is_valid(), user_form.is_valid())):
        profile_form.save()
        user_form.save()

    context.update(getUserProfileFormContext(user_form, profile_form))
    return render(request, template_name, context)


@login_required
def about_view(request):
    return render(request, "user/views/about.html", {"title": "About"})

@login_required
def awaiting_approval_view(request):
    return render(request, 'user/views/awaiting_approval.html', {})
