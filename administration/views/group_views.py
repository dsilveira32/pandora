from django.shortcuts import render

from administration.context_functions import *
from administration.views.general import superuser_only
from shared.forms import GroupCreateForm


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

# Admin Groups Detail
@superuser_only
def detail_dashboard_view(request, group_id):
	template_name = 'admin/views/groups/detail_dashboard.html'
	context = {}
	group = getGroupByID(group_id)
	user_profiles = getUserProfilesFromGroup(group)
	context.update(getAdminGroupDetailLayoutContext(group))
	context.update(getAdminGroupUserListContext(user_profiles))

	return render(request, template_name, context)
