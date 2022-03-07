import csv
from errno import ESTALE
import io

from django.contrib.auth.models import User
from django.db.models import Max
from django.shortcuts import render

from administration.context_functions import *
from administration.views.general import superuser_only
from shared.forms import ContestModelForm
from django.http import HttpResponse

from shared.routines import *
from django.core import serializers
import json


#############################
#       CONTEST VIEWS       #
#############################



# Admin contest general view (list of contests)
@superuser_only
def dashboard_view(request):
	template_name = 'admin/pages/contests/dashboard.html'
	context = {}
	contests = getContestsForAdmin(request)

	context.update(getAdminContestNonDetailLayoutContext())
	context.update(getAdminContestListContext(contests))
	return render(request, template_name, context)

# Admin Contest Create
@superuser_only
def create_view(request):
	template_name = 'admin/pages/contests/create.html'
	context = {}
	form = ContestModelForm(request.POST or None)
	if form.is_valid():
		if form.submit():
			return redirect(dashboard_view)

	context.update(getAdminContestNonDetailLayoutContext())
	context.update(getAdminCreateContestFormContext(form))
	return render(request, template_name, context)


# Admin detail contest home view
@superuser_only
def detail_dashboard_view(request, contest_id):
	template_name = 'admin/pages/contests/detail_dashboard.html'
	context = {}
	contest = getContestByID(contest_id)
	submission_count = contest.attempt_set.count()
	team_count = contest.team_set.count()
	test_count = contest.test_set.count()
	ranked_attempts = getAllContestAttemptsRanking(contest)
	# TODO: find a better way to get the user count, maybe its not necessary if prof doesnt want it
	groups = contest.getGroups()
	users = User.objects.filter(group__in=groups)
	user_count = 0
	for u in users:
		user_count += 1

	context.update(getAdminContestRankingsContext(ranked_attempts))
	context.update(getAdminContestDetailLayoutContext(contest))
	context.update(getAdminContestDashboardCardsContext(contest, submission_count, team_count, test_count, user_count))
	return render(request, template_name, context)

# Admin Contest Specification
@superuser_only
def detail_specification_view(request, contest_id):
	template_name = 'admin/pages/contests/detail_specification.html'
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
	template_name = 'admin/pages/contests/edit.html'
	context = {}
	contest = Contest.getByID(contest_id)
	form = ContestModelForm(request.POST or None, instance=contest)
	if form.is_valid():
		if form.submit(contest_id=contest.id):
			return redirect(dashboard_view)

	context.update(getAdminContestDetailLayoutContext(contest))
	context.update(getAdminCreateContestFormContext(form))
	return render(request, template_name, context)


# extract grades
@superuser_only
def extract_grades(request, contest_id):
    # get the contest
    contest = Contest.getByID(contest_id)

    # create the HttpResponse object with the appropriate csv header.

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename = "Contest_"' + str(
        contest.id) + '""' + contest.short_name + '".csv"'

    # get the values needed to be inserted in the csv
    # TODO: making this SQL sector

    query = "select ut.id, ut.number as student_number, ut.name team_name, ut.first_name, ut.last_name, gg.grade, gg.atempts as n_atempts " \
            "from (" \
                "select t.id, t.name, u.first_name, u.last_name, p.number " \
                "from shared_team_users tm " \
                "inner join shared_team t on tm.team_id = t.id " \
                "inner join auth_user u on u.id = tm.user_id " \
                "inner join shared_profile p on p.user_id = u.id " \
                f"where t.contest_id = {contest_id}) as ut " \
            "left join (" \
                "select ca.grade, maxs.atempts, maxs.team_id " \
                f"from (select max(id) as id, count(id) as atempts, team_id from shared_attempt where contest_id = {contest_id} group by team_id) maxs " \
                "inner join shared_attempt ca on ca.id = maxs.id) gg on gg.team_id = ut.id " \
            "order by team_name desc"

    grades = Attempt.objects.raw(query)

    writer = csv.writer(response, delimiter=";", dialect="excel")

    writer.writerow(['student_number', 'team_name', 'team_id', 'first_name', 'last_name', 'grade', 'n_attempts'])

    for g in grades:
        writer.writerow([g.student_number,
                         g.team_name,
                         g.id,
                         g.first_name,
                         g.last_name,
                         g.grade,
                         g.n_atempts])

    return response


# extract grades
@superuser_only
def extract_zip(request, contest_id):
    # get the contest
    contest_obj = Contest.getByID(contest_id)
    qs = Attempt.objects.filter(contest=contest_obj).values('team_id').annotate(id=Max('id'))
    qs2 = Attempt.objects.filter(id__in=qs.values('id'))

    zip_buffer = io.BytesIO()

    moss_str = "moss -l c -d "

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for a in qs2:
            if a.file and os.path.isfile(a.file.path):
                in_file = open(os.path.abspath(a.file.path), "rb")  # opening for [r]eading as [b]inary
                data = in_file.read()  # if you only wanted to read 512 bytes, do .read(512)
                in_file.close()

                fdir, fname = os.path.split(a.file.path)
                zip_path = os.path.join(a.team.name, fname)
                zip_file.writestr(zip_path, data)
                moss_str = moss_str + a.team.name + "/*.c "

        zip_file.writestr("moss.txt", moss_str)
    zip_buffer.seek(0)

    resp = HttpResponse(zip_buffer, content_type='application/zip')
    resp['Content-Disposition'] = 'attachment; filename = %s' % str(contest_obj.short_name)+'.zip'
    return resp



# extract grades
@superuser_only
def export_contest(request, contest_id):
    # get the contest
    contest_obj = Contest.getByID(contest_id)

    specs = contest_obj.getSpecifications()
    contest_tests = contest_obj.getTests()
    data_files = contest_obj.contesttestdatafile_set.all()

    contest =  {}
    contest["title"] = contest_obj.title
    contest["short_name"] = contest_obj.short_name
    contest["description"] = contest_obj.description
    contest["sow"] = contest_obj.sow
    contest["start_date"] = str(contest_obj.start_date)
    contest["end_date"] = str(contest_obj.end_date)
    contest["min_team_members"] = str(contest_obj.min_team_members)
    contest["max_team_members"] = str(contest_obj.max_team_members)
    contest["max_classification"] = str(contest_obj.max_classification)
    contest["visible"] = contest_obj.visible
    contest["max_submissions"] = str(contest_obj.max_submitions)
    contest["language"] = contest_obj.language
    contest["tests"] = []

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for test in contest_tests:
            test_specs = test.getSpecifications()

            test2json = {}
            test2json["name"] = test.name
            test2json["mandatory"] = test.mandatory
            test2json["weight_pct"] = str(test.weight_pct)
            test2json["run_arguments"] = test.run_arguments
            test2json["view_diff"] = test.view_diff
            test2json["view_args"] = test.view_args
            test2json["view_error"] = test.view_error
            test2json["description"] = test.name # change to description
            if test_specs is not None:
                test2json["specs"] = {}
                test2json["specs"]["cpu"] = str(test_specs.cpu)
                test2json["specs"]["mem"] = str(test_specs.mem)
                test2json["specs"]["run_arguments"] = test_specs.run_arguments
                test2json["specs"]["timeout"] = str(test_specs.timeout)
                test2json["specs"]["compile_flags"] = test_specs.compile_flags
                test2json["specs"]["linkage_flags"] = test_specs.linkage_flags
                test2json["specs"]["fsize"] = str(test_specs.fsize)
                test2json["specs"]["check_leak"] = test_specs.check_leak


            if test.input_file and os.path.isfile(test.input_file.path):
                in_file = open(os.path.abspath(test.input_file.path), "rb")
                data_in = in_file.read()
                in_file.close()
                zip_file.writestr(f"{test.name}.in", data_in)

                in_file = open(os.path.abspath(test.input_file.path), "r")
                lines = in_file.readlines()
                test2json["input"] = lines


            if test.output_file and os.path.isfile(test.output_file.path):
                out_file = open(os.path.abspath(test.output_file.path), "rb")
                data_out = out_file.read()
                out_file.close()
                zip_file.writestr(f"{test.name}.out", data_in)
                out_file = open(os.path.abspath(test.output_file.path), "r")
                lines = out_file.readlines()
                test2json["output"] = lines

            contest["tests"].append(test2json)

        if data_files:
            contest["dataFiles"] = []

        for dfile in data_files:
            data_file = open(os.path.abspath(dfile.data_file.path, "rb"))
            data_file_data = in_file.read()
            data_file.close()
            zip_file.writestr(dfile.data_file, data_file_data)
            contest["dataFiles"].append(dfile.data_file)

        zip_file.writestr(f"{contest_obj.short_name}.nfo", json.dumps(contest, indent=4))

    zip_buffer.seek(0)

    resp = HttpResponse(zip_buffer, content_type='application/zip')
    resp['Content-Disposition'] = 'attachment; filename = %s' % str(contest_obj.short_name)+'.zip'
    return resp
