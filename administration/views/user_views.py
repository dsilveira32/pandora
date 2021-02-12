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
    if request.POST:
        action = request.POST.get("action")
        if action:
            for user_id in request.POST.getlist("user_id"):
                user = User.objects.get(id=user_id)
                if action == "validate":
                    user.profile.setValid(True)
                if action == "invalidate":
                    user.profile.setValid(False)
                user.save()

    return render(request, template_name, context)