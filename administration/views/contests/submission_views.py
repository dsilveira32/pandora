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

    context.update(getAdminContestDetailLayoutContext(contest))
    context.update(getAdminContestSubmissionListContext(submissions))

    return render(request, template_name, context)

@superuser_only
def details_view(request, contest_id, attempt_id):
    template_name = 'admin/views/contests/submissions/details.html'
    context = {}
    contest:Contest = getContestByID(contest_id)
    attempt = Attempt.getById(attempt_id)
    submissions = contest.getSubmissions()

    context.update(getAdminContestDetailLayoutContext(contest))
    context.update(getAdminContestSubmissionListContext(submissions))

    return render(request, template_name, context)