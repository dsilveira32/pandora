from django.contrib.auth.models import User
from django.shortcuts import render

from administration.context_functions import *
from administration.views.general import superuser_only
from shared.forms import ContestModelForm

from shared.routines import *
#############################
#       CONTEST VIEWS       #
#############################

# Admin contest general view (list of contests)
@superuser_only
def dashboard_view(request):
	template_name = 'admin/views/contests/dashboard.html'
	context = {}
	contests = getContestsForAdmin(request)

	context.update(getAdminContestNonDetailLayoutContext())
	context.update(getAdminContestListContext(contests))
	return render(request, template_name, context)

# Admin Contest Create
@superuser_only
def create_view(request):
	template_name = 'admin/views/contests/create.html'
	context = {}
	form = ContestModelForm(request.POST or None)
	if form.is_valid():
		if form.submit(request):
			return redirect(dashboard_view)

	context.update(getAdminContestNonDetailLayoutContext())
	context.update(getAdminCreateContestFormContext(form))
	return render(request, template_name, context)


# Admin detail contest home view
@superuser_only
def detail_dashboard_view(request, contest_id):
	template_name = 'admin/views/contests/detail_dashboard.html'
	context = {}
	contest = getContestByID(contest_id)
	submission_count = contest.attempt_set.count()
	team_count = contest.team_set.count()
	test_count = contest.test_set.count()

	# TODO: find a better way to get the user count, maybe its not necessary if prof doesnt want it
	groups = contest.getGroups()
	users = User.objects.filter(group__in=groups)
	user_count = 0
	for u in users:
		user_count += 1

	context.update(getAdminContestDetailLayoutContext(contest))
	context.update(getAdminContestDashboardCardsContext(contest, submission_count, team_count, test_count, user_count))
	return render(request, template_name, context)

# Admin Contest Specification
@superuser_only
def detail_specification_view(request, contest_id):
	template_name = 'admin/views/contests/detail_specification.html'
	context = {}
	contest = getContestByID(contest_id)
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

	context.update(getAdminContestDetailLayoutContext(contest))
	context.update(getAdminSpecificationFormContext(form))
	return render(request, template_name, context)

# Admin Contest Edit
@superuser_only
def edit_view(request, contest_id):
	template_name = 'admin/views/contests/edit.html'
	context = {}
	contest = Contest.getByID(contest_id)
	form = ContestModelForm(request.POST or None, instance=contest)
	if form.is_valid():
		if form.submit(contest_id=contest.id):
			return redirect(dashboard_view)

	context.update(getAdminContestDetailLayoutContext(contest))
	context.update(getAdminCreateContestFormContext(form))
	return render(request, template_name, context)

