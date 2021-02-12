from django.contrib.auth.models import User
from django.shortcuts import render

from administration.context_functions import getAdminUsersListContext
from contest.admin_views import superuser_only


@superuser_only
def dashboard_view(request):
    template_name = 'admin/views/users/dashboard.html'
    context = {}
    users = User.objects.all()
    context.update(getAdminUsersListContext(users))

    return render(request, template_name, context)