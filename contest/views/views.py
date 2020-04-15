from django.contrib.auth import logout  # last 2 imported
from django.shortcuts import render, redirect


# page logout
def page_logout(request):
	if request.method == "POST":
		logout(request)
		return redirect('home')


# non active view
def nonactive_view(request):
	template_name = 'contest/error.html'
	context = {
		'title': 'Not active',
		'description': 'Your account is not active. Please wait for the administrator to activate your account.'
	}
	return render(request, template_name, context)


"""

	For the sake of helping the debug will create a view in here for everything and then send it to a function with the
same name so it can process the information.
	This view functions only will serve as a bridge between the platform and the "controller"
	
"""
