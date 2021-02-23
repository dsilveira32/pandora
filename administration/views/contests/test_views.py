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

	context.update(getAdminTestListContext(contest_tests))
	form = TestForm(request.POST or None)
	if form.is_valid():
		with transaction.atomic():
			mandatory_ids = request.POST.getlist('mandatory')
			check_leak_ids = request.POST.getlist('check_leak')
			contest_tests.filter(pk__in=mandatory_ids).update(mandatory = True)
			contest_tests.exclude(pk__in=mandatory_ids).update(mandatory = False)
			contest_tests.filter(pk__in=check_leak_ids).update(check_leak = True)
			contest_tests.exclude(pk__in=check_leak_ids).update(check_leak = False)

			type_of_feedback_list = request.POST.getlist('type_of_feedback')
			run_arguments_list = request.POST.getlist('run_arguments')
			weight_pct_list = request.POST.getlist('weight_pct')

			idx = 0
			for t in contest_tests:
				t.type_of_feedback = type_of_feedback_list[idx]
				t.run_arguments = run_arguments_list[idx]
				t.weight_pct = weight_pct_list[idx]

				idx = idx + 1
				t.save()

		contest_tests = contest.test_set.all()
		form = TestForm()
	return render(request, template_name, context)

# Admin create test view
def create_view(request, contest_id):
	template_name = 'admin/views/contests/tests/create.html'
	context = {}
	contest = getContestByID(contest_id)
	context.update(getAdminContestDetailLayoutContext(contest))

	form = CreateTestModelForm(request.POST or None, request.FILES or None)
	# TODO A melhorar
	if form.is_valid():
		submit_passed, override, test = form.submit(contest)
		if submit_passed:
			if override:
				return redirect(detail_specification_view, contest.id, test.getID())
			return redirect(detail_view, contest.id, test.getID())

	###########################
	context.update(getAdminTestFormContext(contest, form))
	return render(request, template_name, context)


# Admin create test view
def detail_view(request, contest_id, test_id):
	template_name = 'admin/views/contests/tests/detail_dashboard.html'
	context = {}
	contest = getContestByID(contest_id)
	context.update(getAdminContestDetailLayoutContext(contest))

	test = Test.objects.get(contest_id=contest_id, id=test_id)

	return render(request, template_name, context)



# Admin Test Specification
@superuser_only
def detail_specification_view(request, contest_id, test_id):
	template_name = 'admin/views/contests/tests/detail_specification.html'
	context = {}
	contest = getContestByID(contest_id)
	context.update(getAdminContestDetailLayoutContext(contest))
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
	context.update(getAdminSpecificationFormContext(form, test))
	return render(request, template_name, context)

# Admin create test view
def detail_edit_view(request, contest_id, test_id):
	template_name = 'admin/views/contests/tests/detail_edit.html'
	context = {}
	contest = getContestByID(contest_id)
	context.update(getAdminContestDetailLayoutContext(contest))

	test = Test.objects.get(contest_id=contest_id, id=test_id)
	form = CreateTestModelForm(request.POST or None, instance=test)

	if form.is_valid():
		submit_passed, override, test = form.submit(contest)
		if submit_passed:
			if override:
				return redirect(detail_specification_view, contest.id, test.getID())
			return redirect(dashboard_view, contest_id)

	context.update(getAdminTestFormContext(contest, form))
	return render(request, template_name, context)
