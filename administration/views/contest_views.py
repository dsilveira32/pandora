from django.shortcuts import render

from administration.context_functions import *
from administration.views.general import superuser_only
from shared.forms import CreateContestModelForm

#############################
#       CONTEST VIEWS       #
#############################

# Admin contest general view (list of contests)
@superuser_only
def dashboard_view(request):
	template_name = 'admin/views/contests/dashboard.html'
	context = {}
	contests = getContestsForAdmin(request)


	context.update(getAdminContestListContext(contests))
	return render(request, template_name, context)

# Admin Contest Create
@superuser_only
def create_view(request):
	template_name = 'admin/views/contests/create.html'
	context = {}
	form = CreateContestModelForm(request.POST or None)
	if form.is_valid():
		if form.submit(request):
			return redirect(dashboard_view)
	context.update(getAdminCreateContestFormContext(form))
	return render(request, template_name, context)


# Admin detail contest home view
@superuser_only
def detail_dashboard_view(request, contest_id):
	template_name = 'admin/views/contests/detail_dashboard.html'
	context = {}
	contest = getContestByID(contest_id)
	context.update(getAdminContestDetailLayoutContext(contest))

	# For list.html
	teams = structureTeamsData(contest.getTeams())
	context.update(getAdminTeamListContext(teams))

	return render(request, template_name, context)

# Admin Contest Specification
@superuser_only
def detail_specification_view(request, contest_id):
	template_name = 'admin/views/contests/detail_specification.html'
	context = {}
	contest = getContestByID(contest_id)
	context.update(getAdminContestDetailLayoutContext(contest))
	specs = contest.getSpecifications()
	form_type = contest.getSpecificationFormType()
	if specs:
		print(1)
		form = form_type(request.POST or None, instance=specs)
	else:
		print(2)
		form = form_type(request.POST or None)
	if form.is_valid():
		if form.submit(contest):
			return redirect(detail_dashboard_view, contest_id)
	context.update(getAdminSpecificationFormContext(form))
	return render(request, template_name, context)

