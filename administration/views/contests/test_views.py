from django.db import transaction
from django.shortcuts import render

from administration.context_functions import *
from administration.views.general import superuser_only
from contest.routines import __get_zip_file_path
from shared.forms import TestForm, CreateTestModelForm
from shared.models import Test


@superuser_only
def dashboard_view(request, contest_id):
	template_name = 'admin/views/contests/tests/dashboard.html'
	context = {}

	contest = getContestByID(contest_id)
	contest_tests = contest.getTests()

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
	# Delete this function when json tests are added
	test_id = 0

	# TODO A melhorar
	if form.is_valid():
		obj = form.save(commit=False)
		zip_in = obj.input_file
		zip_out = obj.output_file
		a_ok = True
		if '.zip' in str(zip_in) and '.zip' in str(zip_out):
			in_files = check_in_files(zip_in, contest)
			in_files.sort(key=natural_keys)
			n_tests = len(in_files)
			out_files = check_out_files(zip_out, contest, n_tests)
			out_files.sort(key=natural_keys)

			if len(in_files) > 0 and len(out_files) > 0:
				for i in range(len(in_files)):
					if not in_files[i].split('.')[0] == out_files[i].split('.')[0]:
						a_ok = False
			else:
				a_ok = False

			if a_ok:
				weight = 100 / n_tests
				benchmark = True
				test_number = 0

				for i in range(n_tests):
					test_number += 1
					form = CreateTestModelForm(request.POST or None, request.FILES or None)
					# test = form.save(commit=False)
					test = Test()
					test.contest = contest
					test.weight_pct = weight
					path = __get_zip_file_path(zip_in) + "/in/" + str(in_files[i])
					f = open(path)
					test.input_file.save(in_files[i], File(f))
					f.close()
					path = __get_zip_file_path(zip_in) + "/out/" + str(out_files[i])
					f = open(path)

					test.output_file.save(out_files[i], File(f))
					f.close()
					if in_files[i].split('.')[1] == "in":
						test.use_for_time_benchmark = False
						test.use_for_memory_benchmark = False
						test.mandatory = False
						test.type_of_feedback = 1
					elif in_files[i].split('.')[1] == "inh":
						test.use_for_time_benchmark = False
						test.use_for_memory_benchmark = False
						test.mandatory = False
						test.type_of_feedback = 2
					elif in_files[i].split('.')[1] == "inm":

						if not benchmark:
							test.use_for_time_benchmark = False
							test.use_for_memory_benchmark = False
							test.mandatory = True
						else:
							test.use_for_time_benchmark = True
							test.use_for_memory_benchmark = True
							test.mandatory = True
							benchmark = False

						test.type_of_feedback = 1
					elif in_files[i].split('.')[1] == "inmh":
						test.use_for_time_benchmark = not not benchmark
						test.use_for_memory_benchmark = not not benchmark
						test.mandatory = not benchmark
						benchmark = not benchmark

						test.type_of_feedback = 2
					test.save()
					test_id = test.id
		if a_ok:
			if request.POST.get('override_default_specifications', False):
				return redirect(detail_specification_view, contest.id, test_id)
			return redirect(detail_view, contest.id, test_id)

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
	template_name = 'views/contests/detail_specification.html'
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
			return redirect(detail_view, contest_id, test_id)
	context.update(getAdminSpecificationFormContext(form))
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
		if form.submit(contest):
			return redirect(detail_view, contest_id, test_id)

	context.update(getAdminTestFormContext(contest, form))
	return render(request, template_name, context)
