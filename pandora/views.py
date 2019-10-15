from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required

@login_required
def about_page(request):
	return render(request, "about.html", {"title": "About"})

