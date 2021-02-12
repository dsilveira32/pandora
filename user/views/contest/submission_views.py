from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render
from django.utils.encoding import smart_text

from shared.forms import AttemptModelForm
from user.context_functions import *


# SUMISSION VIEW
from user.views.contest_views import user_has_contest

# TODO: Create user_has_submission decorator

@login_required
@user_has_contest
def submit_view(request, contest_id):
    checkUserProfileInRequest(request)
    template_name = 'user/views/contests/submission.html'
    context = {}
    can_submit = True

    contest = getContestByID(contest_id)

    # Check team members when user doenst have team
    if not contest.userHasTeam(request.user):
        return redirect(os.path.join(contest.get_absolute_url(), 'team/join/'))

    team = contest.getUserTeam(request.user)
    attempts = team.getAttempts()

    # this will allow specific users to submit outside the scheduled dates
    # example is a user that was sick
    #if not checkUsersDateExceptions(request, contest):
    #    return redirect(os.path.join(contest.get_absolute_url()))

    # Check attempts
    can_submit = contest.checkAttempts(request.user)

    # Check contest
    can_submit = contest.isOpen()

    # Check team
    can_submit = team.getUsers().count() > 0

    # Form Submit
    form = AttemptModelForm(request.POST or None, request.FILES or None)
    submitted, attempt = form.submit(request.user, can_submit, contest, team)
    print_variable_debug(attempt)
    if submitted and attempt:
        handle_uploaded_file(attempt, attempt.file, contest)
        return redirect(detail_view, contest_id, attempt.id)

    context.update(getContestDetailLayoutContext(contest))
    context.update(getContestFormContext(contest, form))
    context.update(getTeamSubmissionHistoryContext(attempts))
    return render(request, template_name, context)

@login_required
@user_has_contest
def detail_view(request, contest_id, submission_id):
    print("Contest ID: %i | Attempt ID: %i" % (contest_id, submission_id))
    checkUserProfileInRequest(request)
    template_name = 'user/views/contests/submission.html'
    context={}

    attempt = getAttemptByID(submission_id)
    contest = getContestByID(contest_id)

    # check if the url contest id is the same of the attempt contest id
    if not contest.id == attempt.getContest().id:
        raise Http404

    team = attempt.getTeam()
    # check if request.user is a member of atempt team OR admin
    if not request.user.is_superuser:
        if not team.hasUser(request.user):
            raise Http404

    results = attempt.getClassifications()
    n_tests, n_mandatory, n_diff = contest.getTestsCount()
    n_passed, mandatory_passed, passed_diff = attempt.getPassedTestsCount()

    for res in results:
        res.expected_output = smart_text(res.test.output_file.read(), encoding='utf-8', strings_only=False,
                                         errors='strict')
        if res.output and os.path.isfile(res.output.path):
            res.obtained_output = smart_text(res.output.read(), encoding='utf-8', strings_only=False, errors='strict')
        else:
            res.obtained_output = ''

        res.input = smart_text(res.test.input_file.read(), encoding='utf-8', strings_only=False,
                               errors='strict')

    # res.diff = ' '.join(map(str, res.diff))
    context.update(getTeamSubmissionDetailsContext(contest, request.user, team, attempt, n_passed, n_tests, mandatory_passed, n_mandatory, passed_diff, n_diff, results, "9"))
    context.update(getContestDetailLayoutContext(contest))
    context.update(getTeamSubmissionHistoryContext(team.getAttempts()))
    return render(request, template_name, context)

