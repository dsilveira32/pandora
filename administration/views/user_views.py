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
            is_submit_ok, user = userForm.submit()
            if is_submit_ok:
                if profileForm.submit():
                    context.update({"message": "User\'s data saved successfully.", "type": "success"})
                else:
                    context.update({"message": "An error occurred when saving user\'s profile data", "type": "danger"})
            else:
                context.update({"message": "An error occurred when saving user\'s data", "type": "danger"})
        context.update(getAdminUserDetailLayoutContext(user))
        context.update(getAdminUsersFormContext(userForm, profileForm))
    else:
        context.update({"message": "User doesn\'t exists!", "type": "danger"})
    return render(request, template_name, context)

@superuser_only
def user_form_create_view(request):
    template_name = 'admin/views/users/user_form.html'
    context = {}
    userForm = AdminUserEditForm(request.POST or None)
    profileForm = AdminUserProfileEditForm(request.POST or None)
    if request.POST:
        if userForm.is_valid() and profileForm.is_valid():
            is_submit_ok, user = userForm.submit()
            if is_submit_ok:
                profileForm = AdminUserProfileEditForm(request.POST or None, instance=user.profile)
                if profileForm.submit():
                    return redirect("admin_users_home")
                else:
                    context.update({"message": "An error occurred when saving user\'s profile data", "type": "danger"})
            else:
                context.update({"message": "An error occurred when saving user\'s data", "type": "danger"})
        else:
            context.update({"message": "Please fill all mandatory fields!", "type": "danger"})

    context.update(getAdminUsersFormContext(userForm, profileForm))
    return render(request, template_name, context)
