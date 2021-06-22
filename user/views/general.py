from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from shared.routines import *
from shared.forms import ProfileModelForm, UserModelForm
from user.context_functions import *
from user.views import contest_views
from django.utils import timezone


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

def user_complete_profile_required(function):
    """
    Redirects the user if the own profile is not complete
    """
    def _inner(request, *args, **kwargs):
        if not request.user.profile.gprd or not request.user.profile.getNumber() or not request.user.first_name:
            return redirect(profile_view)
        return function(request, *args, **kwargs)
    return _inner


@login_required
@user_complete_profile_required
@user_approval_required
def dashboard_view(request):
    #return redirect(contest_views.dashboard_view)
    template_name = 'user/pages/dashboard.html'
    context = {}
    contests = Contest.getContestsForUser(request)

    context.update(getUserGradesDasboardContext(request))
    context.update(getUserDashboardOngoingContestsProgressContext(contests))
    context.update(getUserContestsNumberCardContext(request))
    context.update(getUserDashboardAvgGradeCardContext(request, contests))
    context.update(getUserDashboardAvgNumbSubmissionsCardContext(request, contests))
    context.update(getUserDashboardAvgRankingCardContext(request, contests))
    return render(request, template_name, context)


@login_required
def profile_view(request):
    template_name = 'user/pages/profile.html'
    context = {}
    profile_form = ProfileModelForm(request.POST or None, instance=request.user.profile)
    user_form = UserModelForm(request.POST or None, instance=request.user)

    if all((profile_form.is_valid(), user_form.is_valid())):
        profile_form.save()
        user_form.save()
        return redirect(dashboard_view)

    context.update(getUserProfileFormContext(user_form, profile_form))
    return render(request, template_name, context)


@login_required
@user_complete_profile_required
def about_view(request):
    return render(request, "user/pages/about.html", {"title": "About"})

@login_required
@user_complete_profile_required
def awaiting_approval_view(request):
    return render(request, 'user/pages/awaiting_approval.html', {})
