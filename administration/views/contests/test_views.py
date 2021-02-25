from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render
from shared.routines import *
from administration.context_functions import *
from administration.views.general import superuser_only
from shared.routines import __get_zip_file_path
from shared.forms import TestForm, CreateTestModelForm
from shared.models import Test


@superuser_only
def dashboard_view(request, contest_id):
	template_name = 'admin/views/contests/tests/dashboard.html'
	context = {}

	contest = getContestByID(contest_id)
	contest_tests = contest.getTests()
	contest_tests.weightSum = Test.objects.aggregate(Sum('weight_pct'))["weight_pct__sum"]
	context.update(getAdminContestDetailLayoutContext(contest))

	context.update(getAdminTestsNonDetailLayoutContext(contest))
	context.update(getAdminTestListContext(contest_tests))
	return render(request, template_name, context)


@superuser_only
def list_edit_view(request, contest_id):
	template_name = 'admin/views/contests/tests/list_edit.html'
	context = {}
	contest = getContestByID(contest_id)
	contest_tests = contest.getTests()
	form = TestForm(request.POST or None)
	if form.is_valid():
		with transaction.atomic():
			mandatory_ids = request.POST.getlist('mandatory')
			contest_tests.filter(pk__in=mandatory_ids).update(mandatory=True)
			contest_tests.exclude(pk__in=mandatory_ids).update(mandatory=False)
			weight_pct_list = request.POST.getlist('weight_pct')
			name_list = request.POST.getlist('name')
			idx = 0
			for t in contest_tests:
				t.weight_pct = weight_pct_list[idx]
				t.name = name_list[idx]
				idx = idx + 1
				t.save()
			return redirect(dashboard_view, contest_id)
	context.update(getAdminTestsNonDetailLayoutContext(contest))
	context.update(getAdminTestsListEditFormContext(contest_tests))
	return render(request, template_name, context)

# Admin create test view
@superuser_only
def create_view(request, contest_id):
	template_name = 'admin/views/contests/tests/create.html'
	context = {}
	contest = getContestByID(contest_id)

	form = CreateTestModelForm(request.POST or None, request.FILES or None)
	# TODO A melhorar
	if form.is_valid():
		submit_passed, override, test = form.submit(contest)
		if submit_passed:
			if override:
				return redirect(detail_specification_view, contest.id, test.getID())
			return redirect(detail_view, contest.id, test.getID())

	###########################
	context.update(getAdminTestsNonDetailLayoutContext(contest))
	context.update(getAdminTestFormContext(contest, form))
	return render(request, template_name, context)


# Admin create test view
@superuser_only
def detail_view(request, contest_id, test_id):
	template_name = 'admin/views/contests/tests/detail_dashboard.html'
	context = {}
	contest = getContestByID(contest_id)
	test = Test.getByID(test_id)
	context.update(getAdminTestDetailLayoutContext(contest, test))
	context.update(getAdminTestDetailsContext(test))
	return render(request, template_name, context)



# Admin Test Specification
@superuser_only
def detail_specification_view(request, contest_id, test_id):
	template_name = 'admin/views/contests/tests/detail_specification.html'
	context = {}
	contest = getContestByID(contest_id)
	test = Test.objects.get(id=test_id)
	specs = test.getSpecifications()
	form_type = test.getSpecificationFormType()
	if specs:
		form = form_type(request.POST or None, instance=specs)
	else:
		form = form_type(request.POST or None)
	if form.is_valid():
		if form.submit(test):
			return redirect(dashboard_view, contest_id)

	context.update(getAdminTestDetailLayoutContext(contest, test))
	context.update(getAdminSpecificationFormContext(form))
	return render(request, template_name, context)

# Admin create test view
@superuser_only
def detail_edit_view(request, contest_id, test_id):
	template_name = 'admin/views/contests/tests/detail_edit.html'
	context = {}
	contest = getContestByID(contest_id)

	test = Test.objects.get(contest_id=contest_id, id=test_id)
	form = CreateTestModelForm(request.POST or None, instance=test)

	if form.is_valid():
		submit_passed, override, test = form.submit(contest)
		if submit_passed:
			if override:
				return redirect(detail_specification_view, contest.id, test.getID())
			return redirect(dashboard_view, contest_id)

	context.update(getAdminTestDetailLayoutContext(contest, test))
	context.update(getAdminTestFormContext(contest, form))
	return render(request, template_name, context)
