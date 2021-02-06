from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required



def manage(request):
    return render(request, 'manage.html')


@login_required
def home(request):
    return render(request, 'core/contest_detail_home.html')
