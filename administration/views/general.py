from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from administration.context_functions import *

def superuser_only(function):
	"""Limit view to superusers only."""
	def _inner(request, *args, **kwargs):
		if not request.user.is_superuser:
			raise PermissionDenied
		return function(request, *args, **kwargs)
	return _inner


@superuser_only
def dashboard_view(request):
	template_name = 'admin/views/dashboard.html'
	context = {}
	context.update(getAdminDashboardActiveContestsCardContext())
	context.update(getAdminDashboardLastWeekSubmissionsCardContext())
	context.update(getAdminDashboardActiveUsersCardContext())

	return render(request, template_name, context)