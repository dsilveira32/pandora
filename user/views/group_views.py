from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from shared.forms import GroupJoinForm
from user.context_functions import *

from user.views.general import user_approval_required, user_complete_profile_required


def user_belongs_to_group(function):
    """Limit view to users that belong to the group."""

    def _inner(request, *args, **kwargs):
        group_id = kwargs.get('group_id')
        group = Group.getByID(group_id)
        if group:
               if group.hasUser(request.user):
                   return function(request, *args, **kwargs)
        raise PermissionDenied

    return _inner

##########
# GROUPS #
##########


@login_required
@user_complete_profile_required
@user_approval_required
def dashboard_view(request):
    template_name = 'user/views/groups/dashboard.html'

    context = {}
    groups = getGroupsForUser(request)

    context.update(getUserGroupListContext(groups))
    return render(request, template_name, context)


@login_required
@user_complete_profile_required
@user_approval_required
def join_view(request):
    template_name = 'user/views/groups/join.html'

    context = {}
    form = GroupJoinForm(request.POST or None)
    if request.POST:
        if form.is_valid():
            print('form is valid')
            if form.submit(request.user):
                return redirect(dashboard_view)
        else:
            print('not valid')
            print(form.errors)

    context.update(getUserGroupJoinFormContext(form))
    return render(request, template_name, context)

@login_required
@user_complete_profile_required
@user_approval_required
@user_belongs_to_group
def detail_dashboard_view(request, group_id):
    template_name = 'user/views/groups/detail.html'
    context = {}
    group = Group.objects.get(id=group_id)
    contests = group.getContests()
    context.update(getUserGroupDetailLayout(group))
    context.update(getContestListContext(contests))
    return render(request, template_name, context)