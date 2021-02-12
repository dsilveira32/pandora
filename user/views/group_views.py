from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from shared.forms import GroupJoinForm
from user.context_functions import *

# TODO create user_has_group decorator

##########
# GROUPS #
##########
from user.views.general import user_approval_required


@login_required
@user_approval_required
def dashboard_view(request):
    template_name = 'user/views/groups/dashboard.html'

    context = {}
    groups = getGroupsForUser(request)

    context.update(getUserGroupListContext(groups))
    return render(request, template_name, context)


@login_required
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
@user_approval_required
def detail_dashboard_view(request, group_id):
    template_name = 'doesnt_exist_yet.html'

    context = {}
    return render(request, template_name, context)