from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
# Create your views here.
from django.contrib import auth

from shared.forms import ProfileRegisterForm, UserRegisterForm
from shared.models import Profile


class LoginException(BaseException):
    message = None

    def __init__(self, message):
        # override public fields
        self.message = message

    def getMessage(self):
        return self.message


def autenticate(email, password):
    if not email or not password:
        raise LoginException('You did not provide a user or password!')
    user = auth.authenticate(username=email, password=password)
    if user is None:
        raise LoginException('Email and password does not match!')

    # if not user.check_password(password):
    #    raise LoginException('Incorrect password for this user\'s email!')
    return user


def login_view(request):
    template_name = 'registration/login.html'
    context = {}
    if request.POST:
        try:
            user = autenticate(request.POST['email'], request.POST['password'])
            auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect("user_contests_home")
        except LoginException as error:
            context.update({"error": error})
        except:
            context.update({"error": "Unexpected error. Please contact admin!"})
    return render(request, template_name, context)


def register_view(request):
    template_name = 'registration/register.html'
    user_form = UserRegisterForm(request.POST or None)
    profile_form = ProfileRegisterForm()
    if user_form.is_valid():
        submit_is_ok, user = user_form.submit()
        profile_form = ProfileRegisterForm(request.POST or None, instance=user.profile)
        if submit_is_ok and profile_form.is_valid():
            if profile_form.submit():
                auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('user_contests_home')

    context = {
        "userForm": user_form,
        "profileForm": profile_form
    }
    return render(request, template_name, context)
