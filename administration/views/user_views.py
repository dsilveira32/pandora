from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from administration.context_functions import *
from .general import superuser_only
from shared.forms import *


@superuser_only
def dashboard_view(request, pag=1):
    template_name = 'admin/views/users/home.html'
    context = {}
    #n_reg=2
    #f = pag * n_reg if pag > 1 else 0
    #t = f + n_reg
    #users = User.objects.all()[f:t]
    users = User.objects.all()
    form = UserListForm(request.POST or None)
    if form.is_valid():
        form.submit()

    context.update(getAdminUsersListContext(users))
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
