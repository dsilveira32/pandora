from django.utils.encoding import smart_text

import pandora
from administration.views.general import superuser_only
from django.shortcuts import render
from administration.context_functions import *
from shared.routines import *


@superuser_only
def dashboard_view(request, contest_id):
    template_name = 'admin/views/contests/submissions/dashboard.html'
    context = {}
    contest = getContestByID(contest_id)
    submissions = contest.getSubmissions()

    context.update(getAdminSubmissionNonDetailLayoutContext(contest))
    context.update(getAdminContestSubmissionListContext(submissions))
    context.update(getAdminContestSubmissionChartContext(submissions))

    return render(request, template_name, context)

@superuser_only
def details_view(request, contest_id, attempt_id):
    template_name = 'admin/views/contests/submissions/details.html'
    context = {}
    contest = Contest.getByID(contest_id)

    attempt = Attempt.getByID(attempt_id)
    team = attempt.getTeam()
    results = attempt.getClassifications()

    n_tests, n_mandatory, n_diff = contest.getTestsCount()
    n_passed, mandatory_passed, passed_diff = attempt.getPassedTestsCount()

    results

    """for res in results:
        print(pandora.settings.MEDIA_ROOT)
        print(res.test.output_file)
        res.expected_output = smart_text(res.test.output_file.read(), encoding='utf-8', strings_only=False,
                                         errors='strict')
        if res.output and os.path.isfile(res.output.path):
            res.obtained_output = smart_text(res.output.read(), encoding='utf-8', strings_only=False, errors='strict')
        else:
            res.obtained_output = ''
        res.input = smart_text(res.test.input_file.read(), encoding='utf-8', strings_only=False,
                               errors='strict')
    """
    context.update(getAdminSubmissionDetailLayoutContext(contest, attempt))
    context.update(getAdminContestSubmissionDetailsContext(contest, request.user, team, attempt, n_passed, n_tests, mandatory_passed,
                                            n_mandatory, passed_diff, n_diff, results, 9))
    return render(request, template_name, context)