from django.contrib.auth.models import User
from django.shortcuts import render

from administration.context_functions import *
from contest.admin_views import superuser_only
from shared.forms import *


@superuser_only
def dashboard_view(request):
    template_name = 'admin/views/users/home.html'
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

@superuser_only
def user_form_view(request, user_id):
    template_name = 'admin/views/users/user_form.html'
    context = {}
    if User.objects.filter(id=user_id).exists():
        user = User.objects.get(id=user_id)
        userForm = AdminUserEditForm(request.POST or None, instance=user)
        profileForm = AdminUserProfileEditForm(request.POST or None, instance=user.profile)
        if request.POST and userForm.is_valid() and profileForm.is_valid():
            if not userForm.submit():
                context.update({"message": "An error occurred when saving user\'s data", "type": "danger"})
            if not profileForm.submit():
                context.update({"message": "An error occurred when saving user\'s profile data", "type": "danger"})
            context.update({"message": "User\'s data saved successfully.", "type": "success"})
        context.update(getAdminUserDetailLayoutContext(user))
        context.update(getAdminUsersFormContext(userForm, profileForm))

    return render(request, template_name, context)

@superuser_only
def user_form_create_view(request):
    template_name = 'admin/views/users/home.html'
    context = {}
    return render(request, template_name, context)
