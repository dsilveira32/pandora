from django.contrib.auth.models import User
from django.shortcuts import render

from administration.context_functions import *
from administration.views.general import superuser_only
from shared.forms import GroupModelForm, GroupAddUserForm, GroupAddContestForm

from shared.routines import *

####################
# 	   GROUPS	   #
####################

# Admin Groups


@superuser_only
def dashboard_view(request):
	template_name = 'admin/pages/groups/dashboard.html'
	context = {}
	groups = getGroupsForAdmin(request)
	context.update(getAdminGroupListContext(groups))
	return render(request, template_name, context)

# Admin Groups Create
@superuser_only
def create_view(request):
	template_name = 'admin/pages/groups/create.html'
	context = {}
	group_form = GroupModelForm(request.POST or None)
	if group_form.is_valid():
		group = group_form.save(commit=False)
		group.save()
		return redirect(dashboard_view)
	groups = getGroupsForAdmin(request)
	context.update(getAdminCreateGroupFormContext(group_form))
	context.update(getAdminGroupListContext(groups))

	return render(request, template_name, context)

# Admin Groups Dashboard View
@superuser_only
def detail_dashboard_view(request, group_id):
	template_name = 'admin/pages/groups/detail_dashboard.html'
	context = {}
	group = getGroupByID(group_id)
	contests = group.getContests()

	# TODO: Find a better way to do this
	closed_contest_count = 0
	open_contest_count = 0
	user_count = group.getUsers().count()
	print('user count is: ')
	print(user_count)
	for contest in contests:
		if contest.isOpen():
			open_contest_count += 1
		else:
			closed_contest_count += 1

	context.update(getAdminGroupDetailLayoutContext(group))
	context.update(getAdminGroupDashboardCardsContext(group, user_count, open_contest_count, closed_contest_count))

	return render(request, template_name, context)


# Admin Groups Users Manager
@superuser_only
def users_manage_view(request, group_id):
	template_name = 'admin/pages/groups/users/manage.html'
	context = {}
	group = getGroupByID(group_id)
	users_not_in_group = User.objects.exclude(group__users__group__exact=group)
	users_in_group = group.getUsers()
	addremuserform = GroupAddUserForm(request.POST or None)
	if addremuserform.is_valid():
		addremuserform.submit(group)

	context.update(getAdminGroupDetailLayoutContext(group))
	context.update(getAdminGroupUserManagerContext(users_not_in_group, users_in_group))
	return render(request, template_name, context)

# Admin Groups Contests Manager
@superuser_only
def contests_manage_view(request, group_id):
	template_name = 'admin/pages/groups/contests/manage.html'
	context = {}
	group = getGroupByID(group_id)
	contests = Contest.objects.exclude(group__contests__group__exact=group).all()
	contests_in = group.getContests()
	form = GroupAddContestForm(request.POST or None)
	if form.is_valid():
		form.submit(group)
	context.update(getAdminGroupsContestsManagerContext(contests, contests_in))
	context.update(getAdminGroupDetailLayoutContext(group))
	return render(request, template_name, context)

# Admin Groups Edit
@superuser_only
def edit_view(request, group_id):
	template_name = 'admin/pages/groups/edit.html'
	context = {}
	group = getGroupByID(group_id)
	group_form = GroupModelForm(request.POST or None, instance=group)
	if group_form.is_valid():
		group = group_form.save(commit=False)
		group.save()
		return redirect(detail_dashboard_view, group_id = group.id)
	context.update(getAdminCreateGroupFormContext(group_form))
	context.update(getAdminGroupDetailLayoutContext(group))
	return render(request, template_name, context)