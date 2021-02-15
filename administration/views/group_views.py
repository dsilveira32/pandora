from django.contrib.auth.models import User
from django.shortcuts import render

from administration.context_functions import *
from administration.views.general import superuser_only
from shared.forms import GroupCreateForm, GroupAddUserForm

from shared.routines import *

####################
# 	   GROUPS	   #
####################

# Admin Groups


@superuser_only
def dashboard_view(request):
	template_name = 'admin/views/groups/dashboard.html'
	context = {}
	groups = getGroupsForAdmin(request)
	context.update(getAdminGroupListContext(groups))
	return render(request, template_name, context)

# Admin Groups Create
@superuser_only
def create_view(request):
	template_name = 'admin/views/groups/create.html'
	context = {}
	group_form = GroupCreateForm(request.POST or None)
	if group_form.is_valid():
		group = group_form.save(commit=False)
		group.save()
		return redirect(dashboard_view)
	groups = getGroupsForAdmin(request)
	context.update(getAdminCreateGroupFormContext(group_form))
	context.update(getAdminGroupListContext(groups))

	return render(request, template_name, context)

# Admin Groups Users Manager
@superuser_only
def users_manage_view(request, group_id):
	template_name = 'admin/views/groups/users/manage.html'
	context = {}
	group = getGroupByID(group_id)
	users = User.objects.exclude(group__users__group__exact=group)
	user_profiles = getUserProfilesFromGroup(group)
	addremuserform = GroupAddUserForm(request.POST or None)
	if addremuserform.is_valid():
		addremuserform.submit(group)

	context.update(getAdminGroupDetailLayoutContext(group))
	context.update(getAdminGroupUserListContext(user_profiles))
	context.update(getAdminUsersListContext(users))
	return render(request, template_name, context)

# Admin Groups Contests Manager
@superuser_only
def contests_manage_view(request, group_id):
	template_name = 'admin/views/groups/contests/manage.html'
	context = {}
	group = getGroupByID(group_id)
	users = Contest.objects.exclude(group__users__group__exact=group).all()
	contests = group.getContests()
	#form
	context.update(getAdminContestListContext(contests))
	context.update(getAdminGroupDetailLayoutContext(group))
	return render(request, template_name, context)
